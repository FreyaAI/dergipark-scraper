import os
import glob
import json

from tqdm import tqdm


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


def read_articles_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [Article.from_dict(article) for article in json.load(file)]


def get_all_json_files_in_dir(dir_path):
    return glob.glob(os.path.join(dir_path, "*.json"))


def makedirsifnotexists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def main():
    SOURCE_DIR = "dergipark_articles_with_language"
    DEST_DIR = "dergipark_articles_turkish"
    LANGUAGE_WHITELIST = ["turkish"]

    language_counts = {}

    makedirsifnotexists(DEST_DIR)

    filtered_articles = []

    for file_path in tqdm(get_all_json_files_in_dir(SOURCE_DIR)):
        articles = read_articles_from_json(file_path)

        for article in articles:
            if article.language not in language_counts:
                language_counts[article.language] = 0

            else:
                language_counts[article.language] += 1

            if article.language in LANGUAGE_WHITELIST:
                filtered_articles.append(article)

    with open(
        os.path.join(DEST_DIR, "dergipark_articles_turkish"), "w", encoding="utf-8"
    ) as file:
        # Convert each Article object to its dictionary representation
        articles_dict = [article.to_dict() for article in filtered_articles]
        # Write the list of dictionaries to the file in JSON format
        json.dump(articles_dict, file, ensure_ascii=False, indent=4)

    print(language_counts)


if __name__ == "__main__":
    main()
