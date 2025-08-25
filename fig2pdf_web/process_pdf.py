import pikepdf
import json
import subprocess
import shutil
import os
from os.path import abspath, dirname, join, basename

def process_pdf_files(input_pdf_path, color_mapping_path, output_dir, tolerance=0.002):
    logs = []
    success = False
    output_cmyk_pdf = None
    output_final_pdf = None

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define output file paths
    base_name = os.path.splitext(basename(input_pdf_path))[0]
    intermediate_cmyk_pdf = join(output_dir, f'{base_name}_cmyk.pdf')
    final_print_pdf = join(output_dir, f'{base_name}_modern_print.pdf')

    logs.append("--- Step 1: Replacing RGB with CMYK values ---")

    # --- Load Color Mappings ---
    try:
        with open(color_mapping_path, 'r') as f:
            color_mappings_data = json.load(f)['mappings']
    except FileNotFoundError:
        logs.append(f"Error: Mapping file not found at {color_mapping_path}")
        return {"success": False, "message": "\n".join(logs)}
    except (json.JSONDecodeError, KeyError):
        logs.append(f"Error: Could not parse JSON or 'mappings' key not found in {color_mapping_path}")
        return {"success": False, "message": "\n".join(logs)}

    rgb_to_cmyk_map = {}
    for item in color_mappings_data:
        rgb_key = tuple(c / 255.0 for c in item['rgb_255'])
        cmyk_value = tuple(c / 100.0 for c in item['cmyk_100'])
        rgb_to_cmyk_map[rgb_key] = cmyk_value

    logs.append("Color mappings loaded and processed.")

    # --- PDF Processing ---
    intermediate_file_created = False
    try:
        with pikepdf.open(input_pdf_path) as pdf:
            logs.append(f"Successfully opened PDF: {input_pdf_path}")
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
                                if (abs(r - map_rgb[0]) < tolerance and
                                    abs(g - map_rgb[1]) < tolerance and
                                    abs(b - map_rgb[2]) < tolerance):
                                    
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
                        logs.append(f"  Page {i+1}: Replaced {page_replacements} color definitions.")
                        total_replacements += page_replacements
                        new_content = pikepdf.unparse_content_stream(commands)
                        page.Contents = pdf.make_stream(new_content)

                except Exception as e:
                    logs.append(f"  Could not process page {i+1}. Error: {e}")

            if total_replacements > 0:
                logs.append(f"\nTotal replacements made: {total_replacements}")
                pdf.save(intermediate_cmyk_pdf)
                logs.append(f"Successfully saved intermediate PDF to: {intermediate_cmyk_pdf}")
                intermediate_file_created = True
                output_cmyk_pdf = intermediate_cmyk_pdf
            else:
                logs.append("\nNo matching RGB colors found to replace. No files created.")

    except Exception as e:
        logs.append(f"An unexpected error occurred during PDF processing: {e}")
        return {"success": False, "message": "\n".join(logs)}

    if not intermediate_file_created:
        logs.append("No intermediate CMYK file was created, skipping final conversion.")
        return {"success": False, "message": "\n".join(logs)}

    # --- Step 2: Convert to Modern Print-Ready PDF (preserving vectors) ---
    logs.append("\n--- Step 2: Converting to modern print-ready PDF ---")
    
    gs_command = shutil.which('gs')
    if not gs_command:
        logs.append("Warning: Ghostscript ('gs') not found in your system's PATH.")
        logs.append(f"Skipping final conversion. Your intermediate CMYK file is safe at: {intermediate_cmyk_pdf}")
        return {"success": False, "message": "\n".join(logs), "output_cmyk_pdf": output_cmyk_pdf}

    logs.append(f"Found Ghostscript at: {gs_command}")
    logs.append(f"Converting '{intermediate_cmyk_pdf}' to a modern print-ready PDF (preserving vectors)...")

    # New arguments to disable color management and preserve raw CMYK values
    gs_args = [
        gs_command,
        '-dBATCH',
        '-dNOPAUSE',
        '-sDEVICE=pdfwrite',
        '-dUseCIEColor=false',  # Disable advanced color management
        f'-sOutputFile={final_print_pdf}',
        intermediate_cmyk_pdf
    ]

    try:
        process = subprocess.run(gs_args, capture_output=True, text=True, check=True)
        logs.append("\nGhostscript conversion successful!")
        logs.append(f"Final print-ready file created at: {final_print_pdf}")
        output_final_pdf = final_print_pdf
        success = True
    except subprocess.CalledProcessError as e:
        logs.append("\nError: Ghostscript conversion failed.")
        logs.append(f"Return code: {e.returncode}")
        logs.append("--- Ghostscript stdout ---")
        logs.append(e.stdout)
        logs.append("--- Ghostscript stderr ---")
        logs.append(e.stderr)
        logs.append(f"The intermediate file '{intermediate_cmyk_pdf}' was created but the final conversion failed.")
        success = False
    except FileNotFoundError:
        logs.append(f"Error: Could not run Ghostscript command. Is '{gs_command}' correct?")
        success = False
    
    return {
        "success": success,
        "message": "\n".join(logs),
        "output_cmyk_pdf": output_cmyk_pdf,
        "output_final_pdf": output_final_pdf
    }

if __name__ == '__main__':
    # Example usage if run directly (for testing)
    # This part will not be used by the Flask app
    import sys
    if len(sys.argv) != 3:
        print("Usage: python process_pdf.py <input_pdf_path> <color_mapping_path>")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    color_map = sys.argv[2]
    output_dir = os.getcwd() # Or a specific output directory

    result = process_pdf_files(input_pdf, color_map, output_dir)
    print(result["message"])
    if result["success"]:
        print("PDF processing completed successfully.")
        if result["output_cmyk_pdf"]:
            print(f"Intermediate CMYK PDF: {result['output_cmyk_pdf']}")
        if result["output_final_pdf"]:
            print(f"Final Print-Ready PDF: {result['output_final_pdf']}")
    else:
        print("PDF processing failed.")