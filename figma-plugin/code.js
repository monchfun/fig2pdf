// code.js

// Show the plugin UI
figma.showUI(__html__, { width: 340, height: 480, title: "CMYK Color Exporter" });

// Listen for selection changes on the Figma canvas
figma.on('selectionchange', () => {
  const uniqueColors = getUniqueColorsFromSelection();
  figma.ui.postMessage({ type: 'colors-found', colors: uniqueColors });
});

// Listen for messages from the UI
figma.ui.on('message', async (msg) => {
  if (msg.type === 'export-clicked') {
    const { mappings } = msg;

    // 1. Prepare and send the JSON file
    const jsonForScript = { mappings: mappings };
    const jsonString = JSON.stringify(jsonForScript, null, 2);
    figma.ui.postMessage({ type: 'download-json', data: jsonString });
  }
});

/**
 * Traverses the current selection, finds all unique solid paint colors,
 * and returns them as an array of RGB objects.
 */
function getUniqueColorsFromSelection() {
  const selection = figma.currentPage.selection;
  const uniqueColorMap = new Map(); // Map to store unique colors

  function processPaints(paints, uniqueColorMap) {
    for (const paint of paints) {
      if (paint.type === 'SOLID') {
        const rgb = paint.color;
        const colorKey = JSON.stringify(rgb); // Use RGB as key for uniqueness

        if (!uniqueColorMap.has(colorKey)) {
          uniqueColorMap.set(colorKey, { rgb });
        }
      }
    }
  }

  // Recursive function to get paints from all nodes in the selection
  function findPaints(nodes) {
    for (const node of nodes) {
      if ('fills' in node && Array.isArray(node.fills)) {
        processPaints(node.fills, uniqueColorMap);
      }
      if ('strokes' in node && Array.isArray(node.strokes)) {
        processPaints(node.strokes, uniqueColorMap);
      }
      // If the node is a group or frame, look inside it
      if (('children' in node) && (node.type === 'GROUP' || node.type === 'FRAME' || node.type === 'COMPONENT' || node.type === 'INSTANCE')) {
        findPaints(node.children);
      }
    }
  }

  findPaints(selection);

  return Array.from(uniqueColorMap.values());
}

