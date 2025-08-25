"use strict";
// code.ts
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
// Show the plugin UI
figma.showUI(__html__, { width: 340, height: 480, title: "CMYK Color Exporter" });
// Listen for selection changes on the Figma canvas
figma.on('selectionchange', () => {
    const uniqueColors = getUniqueColorsFromSelection();
    figma.ui.postMessage({ type: 'colors-found', colors: uniqueColors });
});
// Listen for messages from the UI
figma.ui.on('message', (msg) => __awaiter(void 0, void 0, void 0, function* () {
    if (msg.type === 'export-clicked') {
        const { mappings } = msg;
        // 1. Prepare and send the JSON file
        const jsonForScript = { mappings: mappings };
        const jsonString = JSON.stringify(jsonForScript, null, 2);
        figma.ui.postMessage({ type: 'download-json', data: jsonString });
        // 2. Prepare and send the PDF file
        const selection = figma.currentPage.selection;
        if (selection.length === 0) {
            figma.notify("Please select a frame or object to export as PDF.", { error: true });
            return;
        }
        // We'll export the first selected node. For better results, users should select a single frame.
        const exportNode = selection[0];
        console.log('Attempting PDF export for node:', exportNode.name); // ADDED LOG
        try {
            const pdfData = yield exportNode.exportAsync({ format: 'PDF' });
            console.log('PDF data received. Size:', pdfData.byteLength); // ADDED LOG
            if (pdfData.byteLength === 0) { // ADDED CHECK FOR EMPTY DATA
                figma.notify("PDF export resulted in empty data. Is the selected frame empty or unexportable?", { error: true });
                return;
            }
            figma.ui.postMessage({ type: 'download-pdf', data: pdfData });
            console.log('Sent PDF data to UI.'); // ADDED LOG
        }
        catch (e) {
            figma.notify(`Error exporting PDF: ${e.message}`, { error: true });
            console.error('PDF export failed in catch block:', e); // ADDED LOG
        }
    }
}));
/**
 * Traverses the current selection, finds all unique solid paint colors,
 * and returns them as an array of RGB objects.
 */
function getUniqueColorsFromSelection() {
    const selection = figma.currentPage.selection;
    const solidPaints = [];
    // Recursive function to get paints from all nodes in the selection
    function findPaints(nodes) {
        for (const node of nodes) {
            if ('fills' in node && Array.isArray(node.fills)) {
                for (const paint of node.fills) {
                    if (paint.type === 'SOLID') {
                        solidPaints.push(paint);
                    }
                }
            }
            if ('strokes' in node && Array.isArray(node.strokes)) {
                for (const paint of node.strokes) {
                    if (paint.type === 'SOLID') {
                        solidPaints.push(paint);
                    }
                }
            }
            // If the node is a group or frame, look inside it
            if (('children' in node) && (node.type === 'GROUP' || node.type === 'FRAME' || node.type === 'COMPONENT' || node.type === 'INSTANCE')) {
                findPaints(node.children);
            }
        }
    }
    findPaints(selection);
    // Use a Set to store unique color strings to handle duplicates
    const uniqueColorStrings = new Set();
    solidPaints.forEach(paint => {
        uniqueColorStrings.add(JSON.stringify(paint.color));
    });
    // Convert the unique strings back to RGB objects
    const uniqueColors = Array.from(uniqueColorStrings).map(str => JSON.parse(str));
    return uniqueColors;
}
