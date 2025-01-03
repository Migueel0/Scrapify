import threading
from django.shortcuts import render
from django.core.paginator import Paginator
from product.models import Product
from utils.scraper import Scraper

def scraper_task(store):
    if store == 'amazon':
        url = 'https://www.amazon.com/'
        scraper = Scraper(url)
        scraper.amazon_scraper()

def scraper(request, store):
    threading.Thread(target=scraper_task, args=(store,)).start()

    return render(request, 'scraper.html')

def get_all_products(request):
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'index.html', {'page_obj': page_obj})
