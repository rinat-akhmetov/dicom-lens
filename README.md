# Ultrasound-Lens

## Overview

Converts ultrasound DICOM images to JPG and runs AI (LLM) analysis of the resulting images, summarizing findings in a streamlined workflow

## Installation

1. Install Python dependencies:
   - pydicom, numpy, Pillow, anthropic, streamlit, tqdm
2. Make sure ANTHROPIC_API_KEY is set in your environment.

## Using uv

You can also use uv to manage or run this project. For instance:

1. Install uv.
2. Run uv with the main.py in this directory.

## Usage

1. Run:
   - python main.py
2. Enter the DICOM folder path in the UI.
3. Click "Process" to convert and analyze images.

## Additional Information

- Images are converted and saved in the "ultrasound_images" folder by default.
- You can also run Streamlit directly with:  
  streamlit run main.py
