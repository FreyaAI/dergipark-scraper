import os
import time
import glob
import argparse

from google.cloud import storage


def upload_files(bucket_name, source_folder):
    """Uploads files to GCS and deletes them from VM upon successful upload."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for local_file in glob.glob(source_folder + "/**", recursive=True):
        if os.path.isfile(local_file):
            remote_path = os.path.join(
                "destination_folder", local_file[1 + len(source_folder) :]
            )
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)
            print(f"Uploaded {local_file} to {remote_path}")

            # Verify upload
            if blob.exists():
                print(f"Verification successful for {local_file}")
                os.remove(local_file)
                print(f"Deleted {local_file}")
            else:
                print(f"Verification failed for {local_file}, not deleted.")


def main(args):
    BUCKET_NAME = args.bucket_name
    SOURCE_FOLDER = args.source_folder

    upload_files(BUCKET_NAME, SOURCE_FOLDER)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b",
        "--bucket-name",
        type=str,
        required=True,
        help="Name of the GCS bucket to upload to.",
    )
    parser.add_argument(
        "-s" "--source-folder",
        type=str,
        required=True,
        help="Path to the folder containing files to upload.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    start_time = time.time()
    args = get_args()
    main(args)
    print(f"Upload time: {time.time() - start_time} seconds")
