import requests
from bs4 import BeautifulSoup

URL = "https://group.kadokawa.co.jp/global/information/news_release/"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; AnimeNewsMonitor/1.0)"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("KADOKAWA page loaded successfully.")
print("Status:", response.status_code)
print("Page title:", soup.title.get_text(strip=True))

# Print links from the page so we can inspect the structure
links = soup.find_all("a")

for link in links:
    title = link.get_text(" ", strip=True)
    href = link.get("href")

    if title and href:
        print(title, "->", href)
