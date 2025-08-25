import pikepdf
import json
import sys
import subprocess
import shutil
from os.path import abspath, dirname, join

# --- Configuration ---
BASE_DIR = dirname(abspath(__file__))
INPUT_PDF = join(BASE_DIR, 'PPT.pdf')
OUTPUT_PDF = join(BASE_DIR, 'PPT_cmyk.pdf')
FINAL_PDF = join(BASE_DIR, 'PPT_modern_print.pdf') # Changed output name
TOLERANCE = 0.002

# --- Step 1: Replace RGB with precise CMYK values ---
print("--- Step 1: Replacing RGB with CMYK values ---")

# --- Load Color Mappings ---
try:
    with open(join(BASE_DIR, 'color_mapping.json'), 'r') as f:
        color_mappings_data = json.load(f)['mappings']
except FileNotFoundError:
    print(f"Error: Mapping file not found at {join(BASE_DIR, 'color_mapping.json')}")
    sys.exit(1)
except (json.JSONDecodeError, KeyError):
    print(f"Error: Could not parse JSON or 'mappings' key not found.")
    sys.exit(1)

rgb_to_cmyk_map = {}
for item in color_mappings_data:
    rgb_key = tuple(c / 255.0 for c in item['rgb_255'])
    cmyk_value = tuple(c / 100.0 for c in item['cmyk_100'])
    rgb_to_cmyk_map[rgb_key] = cmyk_value

print("Color mappings loaded and processed.")

# --- PDF Processing ---
intermediate_file_created = False
try:
    with pikepdf.open(INPUT_PDF) as pdf:
        print(f"Successfully opened PDF: {INPUT_PDF}")
        total_replacements = 0

        for i, page in enumerate(pdf.pages):
            try:
                commands = []
                page_replacements = 0
                
                for operands, operator in pikepdf.parse_content_stream(page):
                    op_str = str(operator)
                    
                    if op_str in ('rg', 'sc', 'scn') and len(operands) >= 3:
                        r, g, b = [float(c) for c in operands[:3]]
                        
                        found_match = False
                        for map_rgb, map_cmyk in rgb_to_cmyk_map.items():
                            if (abs(r - map_rgb[0]) < TOLERANCE and
                                abs(g - map_rgb[1]) < TOLERANCE and
                                abs(b - map_rgb[2]) < TOLERANCE):
                                
                                new_operands = pikepdf.Array(map_cmyk)
                                new_operator = pikepdf.Operator('k') if op_str in ('sc', 'scn') else pikepdf.Operator('K')

                                commands.append((new_operands, new_operator))
                                page_replacements += 1
                                found_match = True
                                break
                        
                        if not found_match:
                            commands.append((operands, operator))
                    else:
                        commands.append((operands, operator))
                
                if page_replacements > 0:
                    print(f"  Page {i+1}: Replaced {page_replacements} color definitions.")
                    total_replacements += page_replacements
                    new_content = pikepdf.unparse_content_stream(commands)
                    page.Contents = pdf.make_stream(new_content)

            except Exception as e:
                print(f"  Could not process page {i+1}. Error: {e}")

        if total_replacements > 0:
            print(f"\nTotal replacements made: {total_replacements}")
            pdf.save(OUTPUT_PDF)
            print(f"Successfully saved intermediate PDF to: {OUTPUT_PDF}")
            intermediate_file_created = True
        else:
            print("\nNo matching RGB colors found to replace. No files created.")

except Exception as e:
    print(f"An unexpected error occurred during PDF processing: {e}")
    sys.exit(1)

if not intermediate_file_created:
    sys.exit(0)

# --- Step 2: Convert to Modern Print-Ready PDF (preserving vectors) ---
print("\n--- Step 2: Converting to modern print-ready PDF ---")

gs_command = shutil.which('gs')
if not gs_command:
    print("Warning: Ghostscript ('gs') not found in your system's PATH.")
    print(f"Skipping final conversion. Your intermediate CMYK file is safe at: {OUTPUT_PDF}")
    sys.exit(0)

print(f"Found Ghostscript at: {gs_command}")
print(f"Converting '{OUTPUT_PDF}' to a modern print-ready PDF (preserving vectors)...")

# New arguments to disable color management and preserve raw CMYK values
gs_args = [
    gs_command,
    '-dBATCH',
    '-dNOPAUSE',
    '-sDEVICE=pdfwrite',
    '-dUseCIEColor=false',  # Disable advanced color management
    f'-sOutputFile={FINAL_PDF}',
    OUTPUT_PDF
]

try:
    process = subprocess.run(gs_args, capture_output=True, text=True, check=True)
    print("\nGhostscript conversion successful!")
    print(f"Final print-ready file created at: {FINAL_PDF}")
except subprocess.CalledProcessError as e:
    print("\nError: Ghostscript conversion failed.")
    print(f"Return code: {e.returncode}")
    print("--- Ghostscript stdout ---")
    print(e.stdout)
    print("--- Ghostscript stderr ---")
    print(e.stderr)
    print(f"The intermediate file '{OUTPUT_PDF}' was created but the final conversion failed.")
except FileNotFoundError:
    print(f"Error: Could not run Ghostscript command. Is '{gs_command}' correct?")
