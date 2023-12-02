import requests
from concurrent.futures import ThreadPoolExecutor
import os
import time

from utility.request_tool import RequestTool

# Constants
URL_LIST_FILE = "info_urls.txt"
DOWNLOAD_DIR = "dergipark_htmls"
MAX_WORKERS = 20
MAX_RETRIES = 3
RETRY_BACKOFF = 0.5  # seconds


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
    def __init__(self, url_list, download_dir):
        self.url_list = url_list
        self.download_dir = download_dir
        self.downloaded_count = 0
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
            if retry_count < MAX_RETRIES:
                print(
                    f"Error downloading {url}: {e}. Retrying... ({retry_count+1}/{MAX_RETRIES})"
                )
                time.sleep(RETRY_BACKOFF * retry_count)
                self.download_url(url, retry_count + 1)
            else:
                print(f"Failed to download {url} after {MAX_RETRIES} retries.")

    def _update_progress(self):
        self.downloaded_count += 1
        progress = (self.downloaded_count / self.total_urls) * 100
        print(f"Progress: {progress:.2f}%")

    def start_download(self):
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            try:
                executor.map(self.download_url, self.url_list)
            except KeyboardInterrupt:
                print("Download interrupted by user. Exiting...")
                executor.shutdown(wait=False)


def read_url_list(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file]


def main():
    REQUEST_FILE = "proxy_file.json"

    request_tool = RequestTool()
    request_tool.read_from_proxy_file(REQUEST_FILE)

    url_list = read_url_list(URL_LIST_FILE)
    downloader = URLDownloader(url_list, DOWNLOAD_DIR)
    downloader.start_download()


if __name__ == "__main__":
    main()
