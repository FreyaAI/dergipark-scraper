from concurrent.futures import ThreadPoolExecutor
import os
import time
import argparse


from utility.request_tool import RequestTool


import unicodedata
import re


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


class URLDownloader:
    def __init__(
        self, url_list, download_dir, max_workers=20, max_retries=3, retry_backoff=0.5
    ):
        self.url_list = url_list
        self.download_dir = download_dir
        self.downloaded_count = 0
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        self.total_urls = len(url_list)
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        self.request_tool = RequestTool()

    def download_url(self, url, retry_count=0):
        try:
            response = self.request_tool.get(url)

            if response.status_code == 200:
                file_name = os.path.join(self.download_dir, f"{slugify(url)}.html")

                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(response.text)

                print(f"Downloaded {url}")
                self._update_progress()
            else:
                raise Exception(f"HTTP Error: {response.status_code}")
        except Exception as e:
            if retry_count < self.max_retries:
                print(
                    f"Error downloading {url}: {e}. Retrying... ({retry_count+1}/{self.max_retries})"
                )
                time.sleep(self.retry_backoff * retry_count)
                self.download_url(url, retry_count + 1)
            else:
                print(f"Failed to download {url} after {self.max_retries} retries.")

    def _update_progress(self):
        self.downloaded_count += 1
        progress = (self.downloaded_count / self.total_urls) * 100
        print(f"Progress: {progress:.2f}%")

    def start_download(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            try:
                executor.map(self.download_url, self.url_list)
            except KeyboardInterrupt:
                print("Download interrupted by user. Exiting...")
                executor.shutdown(wait=False)


def read_url_list(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file]


def main(args):
    # Constants
    PROXY_FILE = args.proxy
    URL_LIST_FILE = args.url_list
    DOWNLOAD_DIR = args.download_dir
    MAX_WORKERS = args.max_workers
    MAX_RETRIES = args.max_retries
    RETRY_BACKOFF = args.retry_backoff

    request_tool = RequestTool()
    request_tool.read_from_proxy_file(PROXY_FILE)

    url_list = read_url_list(URL_LIST_FILE)
    downloader = URLDownloader(
        url_list, DOWNLOAD_DIR, MAX_WORKERS, MAX_RETRIES, RETRY_BACKOFF
    )
    downloader.start_download()


def get_args():
    parser = argparse.ArgumentParser(description="Download HTML files from DergiPark")
    parser.add_argument(
        "-p",
        "--proxy",
        type=str,
        help="Proxy file path",
        default="proxy_list.txt",
    )
    parser.add_argument(
        "-u",
        "--url-list",
        type=str,
        help="URL list file path",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--download-dir",
        type=str,
        help="Download directory",
        default="downloads",
    )
    parser.add_argument(
        "-w",
        "--max-workers",
        type=int,
        help="Maximum number of workers",
        default=20,
    )
    parser.add_argument(
        "-r",
        "--max-retries",
        type=int,
        help="Maximum number of retries",
        default=3,
    )
    parser.add_argument(
        "-b",
        "--retry-backoff",
        type=float,
        help="Retry backoff time in seconds",
        default=0.5,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    main(args)
