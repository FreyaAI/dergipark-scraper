import requests
import json

from bs4 import BeautifulSoup


class Publisher:
    def __init__(self, name, url, article_count):
        self.name = name
        self.url = url
        self.article_count = article_count

    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            "article_count": self.article_count,
        }

    def __dict__(self):
        return self.to_dict()

    def __str__(self) -> str:
        return f"{self.name} ({self.article_count})"

    @classmethod
    def from_dict(cls, json):
        return cls(json["name"], json["url"], json["article_count"])


def fetch_url(url):
    """Fetches the content of a URL and returns it as a string."""
    response = requests.get(url)
    return response.text


def main():
    # kt-widget-18

    main_page = fetch_url("https://dergipark.org.tr/tr/search?q=&section=articles")

    main_soup = BeautifulSoup(main_page, "html.parser")

    drawer = main_soup.find("div", {"class": "kt-widget-18"})

    ##

    publishers = []

    for item in drawer.find_all(
        "div", {"class": "kt-widget-18__item kt-hidden more-item"}
    ):
        # kt-widget-18__orders div

        name = item.find("a").text.strip().replace("\n", " ").replace("\t", " ")

        article_count = item.find("div", {"class": "kt-widget-18__orders"}).text

        if article_count:
            article_count = int(article_count.strip().replace(".", ""))

        publisher = Publisher(
            name=name,
            url=item.find("a")["href"],
            article_count=article_count,
        )

        publishers.append(publisher)

    ## Write all of it to a json file utf-8 encoded

    with open("publishers.json", "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in publishers], f, ensure_ascii=False)


if __name__ == "__main__":
    main()
