import os
import random
import threading
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from product.models import Product
from review.models import Review
from user.models import User
from utils.scraper import Scraper
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser import FuzzyTermPlugin
from whoosh.query import And, Term, NumericRange
from record.views import add_product_to_record
from record.models import Record
from utils.recommendations import getRecommendedItems, topMatches, sim_distance, calculateSimilarItems

def amazon_scraper():
    url = 'https://www.amazon.com/'
    scraper = Scraper(url)
    scraper.amazon_scraper()

def ebay_scraper():
    url = 'https://ebay.com/deals'
    scraper = Scraper(url)
    scraper.ebay_scraper()

def scrape_all():
    threading.Thread(target=amazon_scraper).start()
    threading.Thread(target=ebay_scraper).start()
    
def scraper_task(store):
    if store == 'amazon':
        amazon_scraper()

    elif store == 'ebay':
        ebay_scraper()
        
    elif store == 'all':
        scrape_all()
        
        

@login_required
def scraper(request, store):
    if not request.user.is_superuser:
        raise PermissionDenied 
    threading.Thread(target=scraper_task, args=(store,)).start()

    return render(request, 'scraper.html')


def user_recommendations(user_id,n):
    if user_id:
        user = get_object_or_404(User, id=user_id)
        if Record.objects.filter(user=user).exists():
            record = get_object_or_404(Record, user=user)
        
            user_prefs = {}
            user_prefs.setdefault(user.username, {})
            for prod in record.products.all():
                user_prefs[user.username][prod.id] = float(prod.price[1:].replace(',', ''))
                
            prefs = {}
            prefs.setdefault(user.username,{})
            for prod in Product.objects.all():
                prefs[user.username][prod.id] = float(prod.price[2:].replace(',', ''))
                
            itemMatch = calculateSimilarItems(prefs)
            recommendations = getRecommendedItems(user_prefs, itemMatch, user.username)
            
            recommended_products = [Product.objects.get(id=rec[1]) for rec in recommendations][:n]
            
            return recommended_products


def product_recommendations(product_id):
    product = get_object_or_404(Product, id=product_id)
    
    prefs = {}
    for prod in Product.objects.all():
        if prod.rating is None:
            prod.rating = 0.0
        prefs[prod.id] = {
            'rating': prod.rating,
            'price': float(prod.price[1:].replace(',', ''))
        }
    
    similar_items = topMatches(prefs, product.id,n=6,similarity=sim_distance)
    similar_products = [Product.objects.get(id=sim[1]) for sim in similar_items]
        
    return similar_products
def get_all_products(request):
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    store = request.GET.get('store', '')
    sort_by = request.GET.get('sort_by', '')
    order = request.GET.get('order', 'asc')  # 'asc' (predeterminado) o 'desc'
    valid_sort_fields = ['price', 'rating']
    sort_by = sort_by if sort_by in valid_sort_fields else None
    order_reverse = order == 'desc'  # True si se requiere orden descendente

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
                
            results = searcher.search(
                myquery, 
                limit=None, 
                sortedby=sort_by, 
                reverse=order_reverse
            )
            
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
        
        recommended_products = user_recommendations(request.user.id, 6)
    
        return render(request, 'index.html', {
            'page_obj': page_obj,
            'query': query,
            'min_price': min_price,
            'max_price': max_price,
            'store': store,
            'sort_by': sort_by,
            'order': order,
            'recommended_products': recommended_products
        })
    return render(request, 'index.html')


@login_required
def record_recommendations(request):
    recommendations = user_recommendations(request.user.id,12)
    return render(request,'related_products.html',{'recommendations':recommendations})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    if request.user.is_authenticated:
        add_product_to_record(request, product_id)
    recommended_products = product_recommendations(product_id)
    return render(request, 'product_detail.html', {'product': product, 'reviews': reviews,'recommended_products': recommended_products})

        
