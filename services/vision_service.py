import google.generativeai as genai
import typing_extensions as typing
import json
import os

class PLCTag(typing.TypedDict):
    Name: str
    Path: str
    DataType: str
    LogicalAddress: str
    Comment: str

class TIAAnalysisResult(typing.TypedDict):
    tags: list[PLCTag]
    scl_code: str
    block_name: str

def analyze_image(image_path: str, api_key: str) -> TIAAnalysisResult:
    """
    Analyzes an industrial logic image using Google Gemini and returns structured data.
    Uses the stable google-generativeai library.
    """
    genai.configure(api_key=api_key)
    
    # Verified models available to the user
    # We include the 'models/' prefix as returned by the API list
    candidate_models = [
        'models/gemini-2.0-flash',
        'models/gemini-2.0-flash-001',
        'models/gemini-2.5-flash',
        'models/gemini-flash-latest',
        'models/gemini-1.5-pro-latest'
    ]

    prompt = """
    You are an expert Siemens TIA Portal V20 developer specializing in S7-1200 PLCs. 
    Analyze this image of an industrial logic diagram.
    
    CRITICAL REQUIREMENT: 100% SYNC BETWEEN TAGS AND CODE
    Every symbol used in your SCL code MUST be either:
    a) Declared in the block's interface (VAR_INPUT, VAR_OUTPUT, VAR, VAR_TEMP).
    b) Included in the 'tags' list as a Global PLC Tag.

    Your task is to:
    1. Identify all Inputs, Outputs, and Memory tags. 
    2. Assign a logical address (e.g., %I0.0, %Q0.0).
    3. Generate the COMPLETE SCL source code for a FUNCTION_BLOCK.
    4. Ensure that the names used in the SCL code (e.g., #myLocalVar or "MyGlobalTag") match EXACTLY the names in the tags list or interface declarations.
    5. For Global Tags, use double quotes in SCL: "TagName". For local variables, optional but recommended: #VariableName.

    Return a JSON object with:
    - tags: A list of Global PLC tags (Excel table).
        - Name, Path, DataType, LogicalAddress, Comment.
    - scl_code: The COMPLETE SCL code.
        - Start with `FUNCTION_BLOCK "BlockName"`
        - Declare ALL used variables in sections (VAR_INPUT, VAR_OUTPUT, VAR, VAR_TEMP).
        - If a variable refers to a Global Tag from the Excel list, ensure the name is IDENTICAL.
        - Write the logic between `BEGIN` and `END_FUNCTION_BLOCK`.
    - block_name: The name of the Function Block (PascalCase).
    """

    with open(image_path, 'rb') as img_file:
        image_data = img_file.read()

    last_error = None
    
    for model_name in candidate_models:
        print(f"Trying model: {model_name}...")
        try:
            model = genai.GenerativeModel(model_name,
                generation_config={"response_mime_type": "application/json", "response_schema": TIAAnalysisResult}
            )
            response = model.generate_content([
                {'mime_type': 'image/jpeg', 'data': image_data},
                prompt
            ])
            print(f"Success with model: {model_name}")
            return json.loads(response.text)
        except Exception as e:
            print(f"Failed with model {model_name}: {e}")
            last_error = e
            continue
            
    if last_error:
        raise last_error
    else:
        raise Exception("No suitable model found.")
