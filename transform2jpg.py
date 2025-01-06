import os

import numpy as np
import pydicom
from PIL import Image


def dicom_to_jpg(dicom_path, jpg_path):
    """
    Converts a single DICOM file to a JPEG image.

    Parameters:
    - dicom_path: Path to the input DICOM file.
    - jpg_path: Path where the output JPEG will be saved.
    """
    try:
        # Read the DICOM file
        dicom = pydicom.dcmread(dicom_path)

        # Extract the pixel data
        pixel_array = dicom.pixel_array

        # Normalize the pixel array to the range 0-255
        # Handle different possible data types
        if pixel_array.dtype != np.uint8:
            pixel_array = pixel_array - np.min(pixel_array)
            pixel_array = (pixel_array / np.max(pixel_array)) * 255
            pixel_array = pixel_array.astype(np.uint8)

        # Convert to PIL Image
        if len(pixel_array.shape) == 2:
            # Grayscale image
            img = Image.fromarray(pixel_array).convert("L")
        elif len(pixel_array.shape) == 3:
            # Color image (e.g., RGB)
            img = Image.fromarray(pixel_array).convert("RGB")
        else:
            print(
                f"Unsupported pixel dimensions: {pixel_array.shape} in file {dicom_path}"
            )
            return

        # Save as JPEG
        img.save(jpg_path, "JPEG")
        print(f"Converted: {dicom_path} -> {jpg_path}")

    except Exception as e:
        print(f"Failed to convert {dicom_path}: {e}")


def convert_dicom_folder_to_jpg(input_folder: str, output_folder: str):
    """
    Converts all DICOM files in the input_folder to JPEG images in the output_folder.

    Parameters:
    - input_folder: Path to the folder containing DICOM files.
    - output_folder: Path to the folder where JPEG images will be saved.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory: {output_folder}")

    # Iterate through all files in the input directory
    for root, _, files in os.walk(input_folder):
        for file in files:
            if True or file.lower().endswith(".dcm"):
                dicom_path = os.path.join(root, file)

                # Create a relative path structure in the output folder
                relative_path = os.path.relpath(root, input_folder)
                output_subfolder = os.path.join(output_folder, relative_path)
                if not os.path.exists(output_subfolder):
                    os.makedirs(output_subfolder)

                # Define the output JPEG path
                jpg_filename = os.path.splitext(file)[0] + ".jpg"
                jpg_path = os.path.join(output_subfolder, jpg_filename)

                # Convert the DICOM file to JPEG
                dicom_to_jpg(dicom_path, jpg_path)


if __name__ == "__main__":
    # input_folder = "IMAGES/DICOMS"
    input_folder = input()
    output_folder = "outputs"

    convert_dicom_folder_to_jpg(input_folder, output_folder)
