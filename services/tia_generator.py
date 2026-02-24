import pandas as pd
import io
import re

def generate_excel(tags_data: list[dict]) -> io.BytesIO:
    """
    Generates an Excel file with the specific columns required by TIA Portal.
    """
    # Map JSON keys to TIA Portal Column Headers
    # JSON: Name, Path, DataType, LogicalAddress, Comment
    # TIA: Name, Path, Data Type, Logical Address, Comment
    
    # Map standard types just in case
    type_map = {
        'Boolean': 'Bool',
        'Integer': 'Int',
        'Real': 'Real',
        'Float': 'Real',
        'String': 'String'
    }

    formatted_data = []
    for tag in tags_data:
        dtype = tag.get('DataType', 'Bool')
        # Capitalize and map
        dtype = dtype.capitalize()
        dtype = type_map.get(dtype, dtype)

        formatted_data.append({
            'Name': tag.get('Name'),
            'Path': tag.get('Path', 'Default tag table'),
            'Data Type': dtype,
            'Logical Address': tag.get('LogicalAddress', ''),
            'Comment': tag.get('Comment', '')
        })
        
    df = pd.DataFrame(formatted_data)
    
    # Ensure column order
    columns = ['Name', 'Path', 'Data Type', 'Logical Address', 'Comment']
    df = df[columns]
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='PLC Tags')
        
        # Add metadata for TIA Portal (Custom Properties)
        # We need to import the property class
        from openpyxl.packaging.custom import StringProperty
        
        workbook = writer.book
        workbook.custom_doc_props.append(StringProperty(name="TIA_Version", value="1.0"))
    
    output.seek(0)
    return output

def generate_scl(analysis_result: dict) -> io.BytesIO:
    """
    Generates a .scl source file for TIA Portal.
    Cleans up the raw LLM output and validates the structure.
    """
    scl_code = analysis_result.get('scl_code', '')
    
    # --- Cleanup Pipeline ---
    
    # 1. Remove markdown code fences (```scl ... ``` or ``` ... ```)
    scl_code = re.sub(r'```[a-zA-Z]*\n?', '', scl_code)
    
    # 2. Fix escaped newlines: LLM sometimes returns literal \n instead of real newlines
    if '\\n' in scl_code and '\n' not in scl_code:
        scl_code = scl_code.replace('\\n', '\n')
    
    # 3. Fix escaped tabs
    scl_code = scl_code.replace('\\t', '\t')
    
    # 4. Strip leading/trailing whitespace
    scl_code = scl_code.strip()
    
    # 5. Normalize line endings to CRLF (TIA Portal on Windows)
    scl_code = scl_code.replace('\r\n', '\n')  # First normalize to LF
    scl_code = scl_code.replace('\r', '\n')     # Handle stray CR
    scl_code = scl_code.replace('\n', '\r\n')   # Convert all to CRLF
    
    # 6. Validate: ensure it ends with END_FUNCTION_BLOCK
    if 'END_FUNCTION_BLOCK' not in scl_code:
        scl_code += '\r\n\r\nEND_FUNCTION_BLOCK\r\n'
    
    # 7. Ensure file ends with a newline
    if not scl_code.endswith('\r\n'):
        scl_code += '\r\n'
    
    # Debug: save a copy for inspection
    try:
        with open('debug_block.scl', 'w', encoding='utf-8-sig') as f:
            f.write(scl_code)
        print(f"[DEBUG] SCL saved to debug_block.scl ({len(scl_code)} chars, {scl_code.count(chr(10))} lines)")
    except:
        pass
    
    output = io.BytesIO()
    # Use utf-8-sig (BOM) for compatibility with Siemens TIA Portal
    output.write(scl_code.encode('utf-8-sig'))
    output.seek(0)
    return output
