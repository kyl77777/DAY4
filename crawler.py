import requests
from bs4 import BeautifulSoup

RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
MAX_ITEMS = 10


def strip_html(text: str) -> str:
    return BeautifulSoup(text or "", "html.parser").get_text(" ", strip=True)


def fetch_news(url: str, limit: int = 10) -> list[dict[str, str]]:
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")[:limit]

    news_list = []
    for item in items:
        title = item.title.get_text(strip=True) if item.title else ""
        summary_raw = item.description.get_text(strip=True) if item.description else ""
        summary = strip_html(summary_raw)
        link = item.link.get_text(strip=True) if item.link else ""
        pub_date = item.pubDate.get_text(strip=True) if item.pubDate else ""

        news_list.append(
            {
                "title": title,
                "summary": summary,
                "link": link,
                "pub_date": pub_date,
            }
        )

    return news_list


def print_news(news_list: list[dict[str, str]]) -> None:
    for i, news in enumerate(news_list, start=1):
        print("=" * 80)
        print(f"[{i}] {news['title']}")
        print(f"발행시간: {news['pub_date']}")
        print(f"링크: {news['link']}")
        print(f"요약: {news['summary']}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        articles = fetch_news(RSS_URL, MAX_ITEMS)
        print_news(articles)
    except requests.RequestException as e:
        print(f"RSS 요청 중 오류가 발생했습니다: {e}")
