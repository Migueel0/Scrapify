import threading
from django.shortcuts import render
from utils.scraper import Scraper

def scraper_task(store):
    if store == 'amazon':
        url = 'https://www.amazon.com/'
        scraper = Scraper(url)
        scraper.amazon_scraper()

def scraper(request, store):
    # Ejecutar el scraping en un hilo separado
    threading.Thread(target=scraper_task, args=(store,)).start()

    return render(request, 'scraper.html')
