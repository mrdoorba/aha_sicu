/**
 * Capture a DOM element containing an SVG chart as a base64 PNG string.
 *
 * Uses the native SVG → Canvas pipeline instead of html-to-image,
 * which crashes on CSS custom properties inside SVG elements.
 */
export async function captureChartAsPng(
  container: HTMLElement,
  pixelRatio = 2,
): Promise<string> {
  const svg = container.querySelector('svg');
  if (!svg) throw new Error('No SVG found in chart container');

  // Clone SVG so we can mutate it without affecting the DOM
  const clone = svg.cloneNode(true) as SVGSVGElement;

  // Resolve CSS variables and computed styles on every element
  const origEls = Array.from(svg.querySelectorAll('*'));
  const cloneEls = Array.from(clone.querySelectorAll('*'));

  for (let i = 0; i < origEls.length; i++) {
    const origEl = origEls[i] as SVGElement;
    const cloneEl = cloneEls[i] as SVGElement;
    const computed = getComputedStyle(origEl);

    // Inline paint attributes that may use CSS variables
    for (const attr of ['fill', 'stroke', 'color', 'stop-color'] as const) {
      const val = cloneEl.getAttribute(attr);
      if (val?.includes('var(') || val === 'currentColor') {
        cloneEl.setAttribute(attr, computed.getPropertyValue(attr) || 'none');
      }
    }

    // Inline font styles for text elements
    if (origEl instanceof SVGTextElement || origEl instanceof SVGTSpanElement) {
      cloneEl.style.fontFamily = computed.fontFamily;
      cloneEl.style.fontSize = computed.fontSize;
      cloneEl.style.fontWeight = computed.fontWeight;
      cloneEl.style.fill = computed.fill;
    }
  }

  // Get dimensions from the original SVG's bounding box
  const { width, height } = svg.getBoundingClientRect();
  clone.setAttribute('width', String(width));
  clone.setAttribute('height', String(height));
  clone.setAttribute('viewBox', `0 0 ${width} ${height}`);

  // Serialize to a data URL
  const serializer = new XMLSerializer();
  const svgString = serializer.serializeToString(clone);
  const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);

  // Draw to canvas
  const canvas = document.createElement('canvas');
  canvas.width = width * pixelRatio;
  canvas.height = height * pixelRatio;
  const ctx = canvas.getContext('2d')!;
  ctx.scale(pixelRatio, pixelRatio);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, width, height);

  return new Promise<string>((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      ctx.drawImage(img, 0, 0, width, height);
      URL.revokeObjectURL(url);
      const dataUrl = canvas.toDataURL('image/png');
      resolve(dataUrl.replace(/^data:image\/png;base64,/, ''));
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Failed to load SVG as image'));
    };
    img.src = url;
  });
}
