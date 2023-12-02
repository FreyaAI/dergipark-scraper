import multiprocessing
import json
import glob
import os
import time

from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime


class Article:
    def __init__(self, title, info_url, abstract):
        self.title = title
        self.info_url = info_url
        self.abstract = abstract

    def to_dict(self):
        return {
            "title": self.title,
            "info_url": self.info_url,
            "abstract": self.abstract,
        }

    def __str__(self) -> str:
        return f"{self.title} ({self.info_url})"

    @classmethod
    def from_dict(cls, json):
        return cls(json["title"], json["info_url"], json["abstract"])


def sanitize(text):
    return text.strip().replace("\n", " ").replace("\t", " ")


def parse_article(soup) -> Article:
    title = None
    info_url = None
    abstract = None

    title_block = soup.find("h5", {"class": "card-title"})
    if title_block:
        title_block = title_block.find("a")
        if title_block:
            title = sanitize(title_block.text)
            info_url = title_block["href"]

    description_block = soup.find("div", {"class": "card-text article-text-block"})

    if description_block:
        abstract = sanitize(description_block.text)

    return Article(title, info_url, abstract)


def extract_articles(html_filepath):
    soup = BeautifulSoup(open(html_filepath, encoding="utf-8"), "html.parser")

    articles = []
    for item in soup.find_all("div", {"class": "card article-card dp-card-outline"}):
        articles.append(parse_article(item))

    return articles


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
            pool.apply_async(extract_articles, (filepath,)) for filepath in filepaths
        ]

        pool.close()  # No more tasks will be submitted to the pool

        # Initialize progress bar
        pbar = tqdm(total=len(filepaths))

        # Collect results and update progress bar
        temp_processed_articles = []
        for result in results:
            articles = result.get()  # Wait for the result
            temp_processed_articles.extend(articles)
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


def main():
    SOURCE_DIR = "C:\Workzone\DergiparkScraper\dergipark_htmls"
    OUTPUT_DIR = "dergipark_articles"
    SAVE_BATCH_SIZE = 50000

    makedirsifnotexists(OUTPUT_DIR)

    filepaths = read_filepaths_from_dir(SOURCE_DIR, "html")

    processor = DataProcessor(OUTPUT_DIR)

    processor.process(filepaths, SAVE_BATCH_SIZE)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Done.")
    print("--- %s seconds ---" % (time.time() - start_time))
