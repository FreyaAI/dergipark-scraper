import os
import json

from tqdm import tqdm

from publisher_finder import Publisher
from utility.request_tool import RequestTool
from landing_scraper import PublisherScraper


def read_json_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def write_to_txt_file_line_by_line(filename, lines):
    with open(filename, "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")


def main():
    publishers = read_json_file("publishers.json")

    publisher_objects = []
    for publisher in publishers:
        publisher_objects.append(Publisher.from_dict(publisher))

    publisher_scarper = PublisherScraper([])

    urls = []

    for publisher in tqdm(publisher_objects):
        urls.extend(
            publisher_scarper.generate_publisher_url_with_pages(
                "https://dergipark.org.tr",
                publisher.url,
                publisher_scarper.calculate_page_count(publisher.article_count),
            )
        )

    write_to_txt_file_line_by_line("urls.txt", urls)


if __name__ == "__main__":
    main()


"""
Example Proxy Usage:
print(
    request_tool.get(
        "https://dergipark.org.tr/tr/search?q=&section=articles&aggs%5Bjournal.id%5D%5B0%5D=284"
    ).text
)
"""
