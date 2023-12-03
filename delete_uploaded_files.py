import os
import time
import argparse

from tqdm import tqdm
from google.cloud import storage


def create_storage_client():
    """Create a Google Cloud Storage client."""
    return storage.Client()


def list_files_in_folder(client, bucket_name, folder_name):
    """List all files in a specific folder of a bucket."""
    bucket = client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(
        prefix=folder_name
    )  # Using prefix to filter for the folder
    return [
        blob.name.split("/")[-1]  # Extracting file name with extension
        for blob in blobs
        if "/" in blob.name and blob.name.endswith("/") is False
    ]


def delete_local_files(file_names, local_directory):
    """Delete files in the local directory that match the provided file names."""
    for file_name in tqdm(file_names):
        local_file_path = os.path.join(local_directory, file_name)
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
            print(f"Deleted {local_file_path}")
        else:
            print(f"File not found: {local_file_path}")


def main(args):
    # Constants
    BUCKET_NAME = args.bucket_name
    FOLDER_NAME = args.folder_name
    LOCAL_DIRECTORY = args.local_directory

    """Main function to list and delete files."""
    client = create_storage_client()
    file_names = list_files_in_folder(client, BUCKET_NAME, FOLDER_NAME)
    delete_local_files(file_names, LOCAL_DIRECTORY)


def parse_args():
    parser = argparse.ArgumentParser(
        description="List and delete files in a Google Cloud Storage bucket."
    )
    parser.add_argument(
        "-b",
        "--bucket_name",
        type=str,
        required=True,
        help="The name of the bucket that contains the files.",
    )
    parser.add_argument(
        "-d",
        "--folder_name",
        type=str,
        required=True,
        help="The name of the folder that contains the files.",
    )
    parser.add_argument(
        "-l",
        "--local_directory",
        type=str,
        required=True,
        help="The path to the local directory that contains the files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    start_time = time.time()
    args = parse_args()
    main(args)
    end_time = time.time()
