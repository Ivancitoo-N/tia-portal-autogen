# TIA Portal Automation App

This local Python/Flask application automates the generation of TIA Portal V20 assets from logic diagrams/screenshots using Google Gemini's multimodal vision capabilities.

## Features
- **Multimodal Input**: Upload screenshots of logic diagrams.
- **PLC Tags Extraction**: Automatically identifies inputs, outputs, and memory tags.
- **SCL Code Generation**: Converts visual logic into structured SCL code.
- **TIA Portal Ready**: Generates `.xlsx` and `.xml` files ready for import into TIA Portal V20.

## Prerequisites
- Python 3.8+
- A Google Gemini API Key

## Installation

1.  Clone the repository or download the source code.
2.  Navigate to the `tia_gen_app` directory.
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the application:
    ```bash
    python app.py
    ```
2.  Open your browser and navigate to `http://localhost:5000`.
3.  Enter your Google Gemini API Key.
4.  Upload a screenshot of your logic.
5.  Wait for the analysis to complete and download the generated files.

## Project Structure
- `app.py`: Main Flask application.
- `services/vision_service.py`: Handles interaction with Google Gemini API.
- `services/tia_generator.py`: Generates Excel and XML files.
- `templates/index.html`: Web interface.
- `static/`: CSS and JavaScript files.
