import multiprocessing
import json
import glob
import os
import time

from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime


class ArticlePair:
    def __init__(self, filename, url):
        self.filename = filename
        self.url = url

    def to_dict(self):
        return {"filename": self.filename, "url": self.url}

    def __str__(self) -> str:
        return f"{self.filename} ({self.url})"

    @classmethod
    def from_dict(cls, json):
        return cls(json["filename"], json["url"])


def sanitize(text):
    return text.strip().replace("\n", " ").replace("\t", " ")


def get_download_url(soup) -> ArticlePair:
    # meta named citation_pdf_url
    download_url = soup.find("meta", {"name": "citation_pdf_url"}).get("content")

    return download_url


def extract_articlepair(html_filepath):
    soup = BeautifulSoup(open(html_filepath, encoding="utf-8"), "html.parser")

    download_url = get_download_url(soup)

    filename = os.path.basename(html_filepath)

    return ArticlePair(filename, download_url)


class DataProcessor:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def save_articles_to_json(self, articles, filename):
        with open(filename, "w", encoding="utf-8") as file:
            # Convert each Article object to its dictionary representation
            articles_dict = [article.to_dict() for article in articles]
            # Write the list of dictionaries to the file in JSON format
            json.dump(articles_dict, file, ensure_ascii=False, indent=4)

    def process(self, filepaths, batch_size=100):
        # Create a pool of workers
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

        # Asynchronously apply `process_file` to each filepath
        results = [
            pool.apply_async(extract_articlepair, (filepath,)) for filepath in filepaths
        ]

        pool.close()  # No more tasks will be submitted to the pool

        # Initialize progress bar
        pbar = tqdm(total=len(filepaths))

        # Collect results and update progress bar
        temp_processed_articles = []
        for result in results:
            articles = result.get()  # Wait for the result
            temp_processed_articles.append(articles)
            pbar.update(1)  # Update progress bar

            if len(temp_processed_articles) >= batch_size:
                self.save_articles_to_json(
                    temp_processed_articles,
                    os.path.join(
                        self.output_dir,
                        f"batch-{datetime.now().strftime('%Y%m%d%H%M%S')}.json",
                    ),
                )
                temp_processed_articles = []

        # Save the remaining articles
        if len(temp_processed_articles) > 0:
            self.save_articles_to_json(
                temp_processed_articles,
                os.path.join(
                    self.output_dir,
                    f"batch-{datetime.now().strftime('%Y%m%d%H%M%S')}.json",
                ),
            )

        pbar.close()


def read_filepaths_from_dir(dir, extension):
    return glob.glob(f"{dir}/*.{extension}")


def makedirsifnotexists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def main(args):
    SOURCE_DIR = args.source_dir
    OUTPUT_DIR = args.output_dir
    SAVE_BATCH_SIZE = args.batch_size

    makedirsifnotexists(OUTPUT_DIR)

    filepaths = read_filepaths_from_dir(SOURCE_DIR, "html")

    processor = DataProcessor(OUTPUT_DIR)

    processor.process(filepaths, SAVE_BATCH_SIZE)


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract article download links from HTML files."
    )

    parser.add_argument(
        "--source_dir",
        type=str,
        required=True,
        help="Directory containing HTML files.",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default="dergipark_article_download_links",
        help="Directory to save the extracted article download links.",
    )

    parser.add_argument(
        "--batch_size",
        type=int,
        default=50000,
        help="Batch size for saving the extracted article download links.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    start_time = time.time()

    args = get_args()
    main(args)
    print("Done.")
    print("--- %s seconds ---" % (time.time() - start_time))
