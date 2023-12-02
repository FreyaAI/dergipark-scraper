import math


class PublisherScraper:
    def __init__(self, publisher_urls) -> None:
        self.publisher_urls = publisher_urls
        pass

    def calculate_page_count(self, article_count: int):
        return math.ceil(article_count / 24)

    def generate_publisher_url_with_pages(self, prefix, publisher_url, page_count):
        def assamble_url(base_url, page):
            parts = base_url.split("/search")

            # Check if the URL is valid and can be split correctly
            if len(parts) != 2:
                raise ValueError("Invalid URL format")

            # Insert the page number
            modified_url = parts[0] + "/search/" + str(page) + parts[1]

            return modified_url

        urls = []
        for i in range(1, page_count + 1):
            urls.append(prefix + assamble_url(publisher_url, i))

        return urls


if __name__ == "__main__":
    publisher_scraper = PublisherScraper(
        publisher_urls=[
            "https://dergipark.org.tr/tr/search?q=&section=articles&aggs%5Bjournal.id%5D%5B0%5D=284"
        ]
    )

    print(
        publisher_scraper.generate_publisher_url_with_pages(
            "https://dergipark.org.tr/tr/search?q=&section=articles&aggs%5Bjournal.id%5D%5B0%5D=284",
            publisher_scraper.calculate_page_count(3159),
        )
    )
