import base64
import logging
import os
import threading
import time
from glob import glob

import anthropic
from tqdm import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def submit_image_analysis_request(image_path) -> str:
    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=ANTHROPIC_API_KEY,
    )
    image_media_type = "image/jpeg"
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    image_prompt: str
    with open("prompts/image_analysis.txt", "r") as f:
        image_prompt = f.read()

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Here is the ultrasound image you need to analyze:",
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": image_prompt,
                    },
                ],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "<ultrasound_analysis>"}],
            },
        ],
    )

    return str(message.content[0].text)


def generate_ultrasound_summary(ultrasound_image_context: str) -> str:
    # Replace placeholders like {{ULTRASOUND_CONTEXT}} with real values,
    # because the SDK does not support variables.
    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=ANTHROPIC_API_KEY,
    )

    prompt: str
    with open("prompts/summary.txt", "r") as f:
        prompt = f.read()
    prompt = prompt.replace("{{ULTRASOUND_IMAGES_ANALYSIS}}", ultrasound_image_context)

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "<ultrasound_analysis>"}],
            },
        ],
    )
    return str(message.content[0].text)


def handle_image_processing(image_path: str) -> bool:
    result = ""
    try:
        result = submit_image_analysis_request(image_path)
    except Exception as e:
        logger.error(f"Failed to process {image_path}: {e}")
        return False
    finally:
        with open(f"results/image_{os.path.basename(image_path)}_result.txt", "w") as f:
            f.write(result)
    return True


def generate_summary():
    result_files = glob("results/image_*_result.txt")
    logger.info(f"Number of files: {len(result_files)}")
    results = []
    for file_path in result_files:
        with open(file_path, "r") as f:
            results.append(f.read())

    combined_text = "\n".join(results)
    with open("combined_text.txt", "w") as f:
        f.write(combined_text)
    final_summary = generate_ultrasound_summary(combined_text)

    with open("result.txt", "w") as f:
        f.write(final_summary)


def execute_file_processing(file_list: list[str]):
    processed_file_results: list[tuple[str, bool]] = []
    for file_path in tqdm(file_list):
        if os.path.isfile(file_path):
            threading.Thread(
                target=lambda: processed_file_results.append(
                    (file_path, handle_image_processing(file_path))
                )
            ).start()
            time.sleep(3.5)
    return processed_file_results


def collect_and_report_analysis(image_dir: str = "outputs"):
    file_paths = [
        os.path.join(image_dir, filename) for filename in os.listdir(image_dir)
    ]
    logger.info(f"Found {len(file_paths)} files in the output directory.")
    file_path_status = execute_file_processing(file_paths)
    failed_file_paths = [
        file_path for file_path, status in file_path_status if not status
    ]
    successful_analysis_count = len(
        list(filter(lambda x: x[1] is True, file_path_status))
    )
    logger.info(f"Number of successful analysis: {successful_analysis_count}")
    logger.info(
        f"Number of failed analysis: {len(file_path_status) - successful_analysis_count}"
    )

    logger.info('Try to fix the failed files and run "process" again.')
    attempt2_file_path_status = execute_file_processing(failed_file_paths)
    attempt2_successful_analysis_count = len(
        list(filter(lambda x: x[1] is True, attempt2_file_path_status))
    )
    logger.info(
        f"Attempt2 Number of successful analysis: {attempt2_successful_analysis_count}"
    )
    logger.info(
        f"Attempt2 Number of failed analysis: {len(failed_file_paths) - attempt2_successful_analysis_count}"
    )
    logger.info("Generate summary for all the files.")
    generate_summary()


if __name__ == "__main__":
    collect_and_report_analysis()
