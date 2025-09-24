import pikepdf
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from collections import Counter
import io

def rgb_to_hex(rgb):
    """Converts an (R, G, B) tuple to a hex string."""
    r, g, b = [max(0, min(255, int(c))) for c in rgb]
    return f'#{r:02x}{g:02x}{b:02x}'

def simple_rgb_to_cmyk(r, g, b):
    """A simple, uncalibrated RGB to CMYK conversion."""
    if (r, g, b) == (0, 0, 0):
        return [0, 0, 0, 100]
    
    c = 1 - r / 255.
    m = 1 - g / 255.
    y = 1 - b / 255.

    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    return [int(c*100), int(m*100), int(y*100), int(k*100)]

def extract_unique_colors(pdf_path, limit=256, quality=75):
    """
    Extracts all unique colors from a PDF, sorted by frequency, and provides a default CMYK conversion.
    """
    all_colors = []

    try:
        with pikepdf.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract vector colors
                try:
                    for operands, operator in pikepdf.parse_content_stream(page):
                        op_str = str(operator)
                        if op_str in ('rg', 'sc', 'scn') and len(operands) >= 3:
                            try:
                                r, g, b = [int(c * 255) for c in operands[:3]]
                                all_colors.append((r, g, b))
                            except (ValueError, TypeError):
                                continue
                except Exception:
                    continue

                # Extract image colors
                for image_obj in page.images.values():
                    try:
                        pil_image = Image.open(io.BytesIO(image_obj.read_raw_bytes()))
                        if pil_image.mode not in ['RGB', 'L']:
                            pil_image = pil_image.convert('RGB')
                        elif pil_image.mode == 'L':
                            pil_image = pil_image.convert('RGB')

                        pil_image.thumbnail((quality, quality))
                        img_colors = np.array(pil_image)
                        pixels = img_colors.reshape(-1, 3)
                        all_colors.extend(map(tuple, pixels))
                    except Exception:
                        continue
    except Exception as e:
        print(f"Error opening or processing PDF {pdf_path}: {e}")
        return []

    if not all_colors:
        return []

    # Count frequency and get the most common colors
    color_counts = Counter(all_colors)
    most_common = color_counts.most_common(limit)
    
    # Prepare the final data structure
    result = []
    for rgb_tuple, count in most_common:
        hex_color = rgb_to_hex(rgb_tuple)
        # Provide a default, simple CMYK conversion
        cmyk_color = simple_rgb_to_cmyk(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
        result.append({
            "hex": hex_color,
            "rgb": rgb_tuple,
            "cmyk": cmyk_color,
            "count": count
        })
    
    return result