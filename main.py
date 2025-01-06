import streamlit as st

from analyse import collect_and_report_analysis
from transform2jpg import convert_dicom_folder_to_jpg


def main():
    st.title("DICOM to JPG Converter & Analysis")
    input_folder: str = str(st.text_input("Enter Path to DICOM Images"))
    if st.button("Process"):
        image_dir = "ultrasound_images"
        convert_dicom_folder_to_jpg(input_folder, image_dir)
        collect_and_report_analysis(image_dir)
        st.success("Processing completed.")


if __name__ == "__main__":
    main()
