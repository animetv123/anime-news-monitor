import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

KADOKAWA_URL = "https://group.kadokawa.co.jp/global/information/news_release/"
STATE_FILE = "kadokawa_seen.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AnimeNewsMonitor/1.0)"
}

# Keywords related to anime, animation and anime IP
ANIME_KEYWORDS = [
    "anime",
    "animation",
    "animated",
    "manga",
    "otaku",
    "animec",
    "studio one base",
    "animation production",
    "anime film",
    "anime event",
    "anime events",
    "voice actor",
    "voice actors",
    "character",
    "visual",
    "production studio",
]


def get_page():
    response = requests.get(
        KADOKAWA_URL,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()
    return response.text


def get_news():
    html = get_page()
    soup = BeautifulSoup(html, "html.parser")

    news = []

    for link in soup.find_all("a", href=True):
        title = link.get_text(" ", strip=True)
        href = link["href"]

        if not title:
            continue

        # We only want actual KADOKAWA news-release pages
        if "/news_release/" not in href:
            continue

        # Skip pagination links
        if "/page/" in href:
            continue

        url = urljoin(KADOKAWA_URL, href)

        # Avoid duplicate links
        if any(item["url"] == url for item in news):
            continue

        news.append({
            "title": title,
            "url": url
        })

    return news


def is_anime_related(title):
    text = title.lower()

    return any(
        keyword in text
        for keyword in ANIME_KEYWORDS
    )


def load_seen():
    if not os.path.exists(STATE_FILE):
        return set()

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return {
            line.strip()
            for line in f
            if line.strip()
        }


def save_seen(seen):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        for url in sorted(seen):
            f.write(url + "\n")


def send_telegram(title, url):
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    message = (
        "🆕 KADOKAWA OFFICIAL\n\n"
        f"📢 {title}\n\n"
        "🔗 Official Source:\n"
        f"{url}"
    )

    telegram_url = (
        f"https://api.telegram.org/bot{bot_token}/sendMessage"
    )

    response = requests.post(
        telegram_url,
        data={
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=30
    )

    response.raise_for_status()


def main():
    print("Checking KADOKAWA official news...")

    news = get_news()

    print(f"Found {len(news)} news articles.")

    seen = load_seen()

    # First run:
    # save existing articles without sending them.
    if not seen:
        print("First run detected.")
        print("Saving existing articles without sending notifications.")

        for item in news:
            seen.add(item["url"])

        save_seen(seen)

        print("Initial database created.")
        return

    new_articles = []

    for item in news:
        if item["url"] not in seen:
            new_articles.append(item)

    print(f"New articles found: {len(new_articles)}")

    for item in new_articles:

        print("\nNEW ARTICLE:")
        print(item["title"])
        print(item["url"])

        if is_anime_related(item["title"]):
            print("Anime-related: YES")
            send_telegram(
                item["title"],
                item["url"]
            )
            print("Telegram notification sent.")

        else:
            print("Anime-related: NO")

        seen.add(item["url"])

    save_seen(seen)

    print("Done.")


if __name__ == "__main__":
    main()
