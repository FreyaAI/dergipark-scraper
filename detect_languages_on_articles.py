import os
import json
import glob
import multiprocessing

from datetime import datetime
from tqdm import tqdm
from typing import List
from lingua import Language, LanguageDetectorBuilder


class Article:
    def __init__(self, title, info_url, abstract, language):
        self.title = title
        self.info_url = info_url
        self.abstract = abstract
        self.language = language

    def to_dict(self):
        return {
            "title": self.title,
            "info_url": self.info_url,
            "abstract": self.abstract,
            "language": self.language,
        }

    def __str__(self) -> str:
        return f"{self.title} ({self.info_url})"

    @classmethod
    def from_dict(cls, json):
        title = json.get("title", None)
        info_url = json.get("info_url", None)
        abstract = json.get("abstract", None)
        language = json.get("language", None)
        return cls(title, info_url, abstract, language)


LANGAUGES = [Language.ENGLISH, Language.TURKISH, Language.AZERBAIJANI]

detector = LanguageDetectorBuilder.from_languages(*LANGAUGES).build()


def language_object_to_string(language):
    if language is None:
        return None

    return str(language).split(".")[1].lower()


def detect_language(article: Article):
    language = detector.detect_language_of(article.title)

    article.language = language_object_to_string(language)

    if article.language is Language.AZERBAIJANI:
        print(f"Detected Azerbaijani: {article}, dadi dadi orospu cocugu")

    return article


class LanguageProcessor:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def save_articles_to_json(self, articles, filename):
        with open(filename, "w", encoding="utf-8") as file:
            # Convert each Article object to its dictionary representation
            articles_dict = [article.to_dict() for article in articles]
            # Write the list of dictionaries to the file in JSON format
            json.dump(articles_dict, file, ensure_ascii=False, indent=4)

    def process(self, articles: List[Article], batch_size=100):
        # Create a pool of workers
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

        # Asynchronously apply `process_file` to each filepath
        results = [
            pool.apply_async(detect_language, (article,)) for article in articles
        ]

        pool.close()  # No more tasks will be submitted to the pool

        # Initialize progress bar
        pbar = tqdm(total=len(articles))

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


def read_articles_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [Article.from_dict(article) for article in json.load(file)]


def get_all_json_files_in_dir(dir_path):
    return glob.glob(os.path.join(dir_path, "*.json"))


def makedirsifnotexists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def main():
    SOURCE_DIR = "dergipark_articles"
    OUTPUT_DIR = "dergipark_articles_with_language"
    BATCH_SIZE = 50000

    makedirsifnotexists(OUTPUT_DIR)

    articles = []
    for file_path in get_all_json_files_in_dir(SOURCE_DIR):
        articles.extend(read_articles_from_json(file_path))

    processor = LanguageProcessor(OUTPUT_DIR)

    processor.process(articles, BATCH_SIZE)


if __name__ == "__main__":
    main()
