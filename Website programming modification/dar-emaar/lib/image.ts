/**
 * Build a Next.js image-optimizer URL for a remote/local image so plain <img>
 * tags get resized + WebP/AVIF compressed (instead of loading 2-3MB originals).
 * Allowed widths must match next.config deviceSizes/imageSizes defaults.
 */
export function optimized(src: string | null | undefined, width = 640, quality = 75): string {
  if (!src) return "";
  if (src.startsWith("data:") || src.startsWith("blob:") || src.startsWith("file:")) return src;
  if (src.toLowerCase().endsWith(".svg")) return src;
  return `/_next/image?url=${encodeURIComponent(src)}&w=${width}&q=${quality}`;
}
