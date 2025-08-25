// code.ts

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
function getUniqueColorsFromSelection(): figma.RGB[] {
  const selection = figma.currentPage.selection;
  const solidPaints: figma.SolidPaint[] = [];

  // Recursive function to get paints from all nodes in the selection
  function findPaints(nodes: readonly SceneNode[]) {
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
  const uniqueColorStrings = new Set<string>();
  solidPaints.forEach(paint => {
    uniqueColorStrings.add(JSON.stringify(paint.color));
  });

  // Convert the unique strings back to RGB objects
  const uniqueColors: figma.RGB[] = Array.from(uniqueColorStrings).map(str => JSON.parse(str));
  
  return uniqueColors;
}