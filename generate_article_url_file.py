import glob
import json

from extract_articles import Article


def read_filepaths_from_dir(dir, extension):
    return glob.glob(f"{dir}/*.{extension}")


def read_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    SOURCE_DIR = "dergipark_articles"

    filepaths = read_filepaths_from_dir(SOURCE_DIR, "json")

    info_urls = []

    for filepath in filepaths:
        json_data = read_json_file(filepath)

        for article_json in json_data:
            info_urls.append(article_json["info_url"])

    with open("info_urls.txt", "w", encoding="utf-8") as file:
        for info_url in info_urls:
            file.write(f"{info_url}\n")


if __name__ == "__main__":
    main()
