import random
import threading
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from product.models import Product
from utils.scraper import Scraper
from utils.whoosh import index_products
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser import FuzzyTermPlugin
from whoosh.query import And, Term, NumericRange

def scraper_task(store):
    if store == 'amazon':
        url = 'https://www.amazon.com/'
        scraper = Scraper(url)
        scraper.amazon_scraper()
    index_products() #Add all products to whoosh index

def scraper(request, store):
    threading.Thread(target=scraper_task, args=(store,)).start()

    return render(request, 'scraper.html')

def get_all_products(request):
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    store = request.GET.get('store', '')
    index_dir = "whoosh_index"
    ix = open_dir(index_dir)
    search_results = []

    with ix.searcher() as searcher:
        query_parser = QueryParser("name", ix.schema)
        query_parser.add_plugin(FuzzyTermPlugin())
        filters = []

        if query:
            filters.append(query_parser.parse(query + '~'))

        if min_price or max_price:
            max_price = float(max_price) if max_price else None
            min_price = float(min_price) if min_price else None
            filters.append(NumericRange("price", min_price, max_price))

        if store:
            filters.append(Term("store", store.lower()))

        if filters:
            myquery = And(filters)
            results = searcher.search(myquery,limit=None)
            for result in results:
                search_results.append({
                    'id': result['id'],
                    'name': result['name'],
                    'price': result['price'],
                    'rating': result['rating'],
                    'image': result['image'],
                    'link': result['link'],
                    'store': result['store']
                })
        else:
            products = Product.objects.all()
            for product in products:
                search_results.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'rating': product.rating,
                    'image': product.image,
                    'link': product.link,
                    'store': product.store
                })
            
    random.seed(4)
    random.shuffle(search_results)
    paginator = Paginator(search_results, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'index.html', {'page_obj': page_obj, 'query': query, 'min_price': min_price, 'max_price': max_price, 'store': store})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})
