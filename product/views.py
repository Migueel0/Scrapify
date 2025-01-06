import os
import random
import threading
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from product.models import Product
from review.models import Review
from utils.scraper import Scraper
from utils.whoosh import index_products
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser import FuzzyTermPlugin
from whoosh.query import And, Term, NumericRange
from record.views import add_product_to_record

def scraper_task(store):
    if store == 'amazon':
        url = 'https://www.amazon.com/'
        scraper = Scraper(url)
        scraper.amazon_scraper()

def scraper(request, store):
    threading.Thread(target=scraper_task, args=(store,)).start()

    return render(request, 'scraper.html')

def get_all_products(request):
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    store = request.GET.get('store', '')
    sort_by = request.GET.get('sort_by', '')
    valid_sort_fields = ['price', 'rating']
    sort_by = sort_by if sort_by in valid_sort_fields else None


    index_dir = "whoosh_index"
    if os.path.exists(index_dir):
        ix = open_dir(index_dir)
        
        search_results = []

        with ix.searcher() as searcher:
            query_parser = QueryParser("name", ix.schema)
            query_parser.add_plugin(FuzzyTermPlugin())
            filters = []

            if query != '':
                key_word = query + '~'
            else:
                key_word = '*'
            
            filters.append(query_parser.parse(key_word))

            if min_price or max_price:
                max_price = float(max_price) if max_price else None
                min_price = float(min_price) if min_price else None
                filters.append(NumericRange("price", min_price, max_price))

            if store:
                filters.append(Term("store", store.lower()))
                
            myquery = And(filters)
                
            results = searcher.search(myquery, limit=None, sortedby=sort_by)
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
        
        if sort_by is None:
            random.seed(4)
            random.shuffle(search_results)

        paginator = Paginator(search_results, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'index.html', {
            'page_obj': page_obj,
            'query': query,
            'min_price': min_price,
            'max_price': max_price,
            'store': store,
            'sort_by': sort_by
        })
    return render(request, 'index.html')


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    add_product_to_record(request, product_id)
    return render(request, 'product_detail.html', {'product': product, 'reviews': reviews})
