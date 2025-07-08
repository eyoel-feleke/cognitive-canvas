import requests
from bs4 import BeautifulSoup

class ContentExtractor:
    def extract_from_url(self, url: str) -> dict:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(strip=True)
        return {"text": text}
