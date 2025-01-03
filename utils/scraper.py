import random
import urllib.request as request
import urllib
from bs4 import BeautifulSoup
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scrapify.settings')
django.setup()

from product.models import Product

USER_AGENTS = [
    
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.102 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.110 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:114.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.1 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36 Edg/114.0.1823.67",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36 Edg/114.0.1823.67",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.110 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.137 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
]


class Scraper:
    def __init__(self, url):
        self.url = url

    def get_html(self, url):
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": url,
        }
        req = request.Request(url, headers=headers)
        try:
            return request.urlopen(req)
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason} for URL: {url}")
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason} for URL: {url}")
        except Exception as e:
            print(f"Unexpected error: {e} for URL: {url}")
        return None
    
    def get_soup(self, url):
        html = self.get_html(url)
        if html is None:
            print(f"Failed to retrieve HTML for URL: {url}. Skipping...")
            return None
        try:
            return BeautifulSoup(html, 'lxml')
        except Exception as e:
            print(f"Error parsing HTML for URL: {url}. Exception: {e}")
            return None
    
    def amazon_scraper(self) -> None:
        base_url = self.url
        soup = self.get_soup(base_url)
        links = []
    
        if soup is None:
            print(f"Failed to scrape base URL: {base_url}")
            return
        
        cards = soup.find_all('div', class_='a-cardui')
        
        for card in cards:
            link = card.find('a', class_='a-link-normal')
            if link:
                link = link['href']
            else:
                continue
            
            links.append(base_url + link)
        i = 0
        for link in links:
            if i == 5: # scrape only 5 items of each link
                break
            i += 1
            
            soup = self.get_soup(link)
            if soup is None:
                print(f"Failed to scrape base URL: {base_url}")
                return
            
            items_cards = soup.find_all('a', class_='a-link-normal s-no-outline')
            items_links = [base_url + item['href'] for item in items_cards]

            for item_link in items_links:
                soup = self.get_soup(item_link)
                try:
                    name = soup.find('span', id='productTitle').text.strip()
                    price = (
                        soup.find('span', class_='a-price-symbol').text +
                        soup.find('span', class_='a-price-whole').text +
                        soup.find('span', class_='a-price-fraction').text
                    )
                    rating = soup.find('span', id='acrPopover')['title'][:3]
                    store = 'Amazon'
                    image = soup.find('img', id='landingImage')['src']
                    link = item_link

                    product = Product(
                        name=name,
                        price=price,
                        rating=rating,
                        store=store,
                        image=image,
                        link=link
                    )
                    if not Product.objects.filter(name=name, price=price, store=store).exists():
                        product.save()

                    print(f"Saved: {product}")
                except Exception as e:
                    print(f"Error saving product: {e}")
        

if __name__ == '__main__':
    url = 'https://www.amazon.com/'
    scraper = Scraper(url)
    scraper.amazon_scraper()
        
        
            
        