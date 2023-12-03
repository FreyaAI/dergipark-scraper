import os
import json
import argparse
import time

from tqdm import tqdm

# Constants


def extract_download_urls(directory, output_file):
    # Collect all file paths in the directory
    file_paths = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, file))
    ]

    with open(output_file, "w") as output:
        for file_path in tqdm(file_paths):
            try:
                with open(file_path, "r") as json_file:
                    data = json.load(json_file)
                    # Extract URLs and write to the output file
                    for item in data:
                        url = item.get("url", "")
                        if url:
                            output.write(url + "\n")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")


def get_args():
    parser = argparse.ArgumentParser(
        description="Extract download URLs from a directory containing JSON files"
    )

    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        required=True,
        help="Path to the directory containing JSON files",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="download_urls.txt",
        help="Path to the output file",
    )

    return parser.parse_args()


def main(args):
    DIRECTORY_PATH = args.directory
    OUTPUT_FILE = args.output

    extract_download_urls(DIRECTORY_PATH, OUTPUT_FILE)


if __name__ == "__main__":
    start_time = time.time()
    args = get_args()
    main(args)

    print(f"Done in {time.time() - start_time} seconds")
