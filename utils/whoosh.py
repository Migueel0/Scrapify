# whoosh_schema.py
from whoosh.fields import Schema, TEXT, NUMERIC
from whoosh.index import create_in
import os

from product.models import Product

def create_index(directory):
    schema = Schema(
        id=NUMERIC(stored=True, unique=True),
        name=TEXT(stored=True),
        price=NUMERIC(stored=True),
        rating=NUMERIC(stored=True),
        image=TEXT(stored=True),
        link=TEXT(stored=True),
        store = TEXT(stored=True)
    )
    if not os.path.exists(directory):
        os.makedirs(directory)
    return create_in(directory, schema)

def index_products():
    index_dir = "whoosh_index"
    ix = create_index(index_dir)
    writer = ix.writer()

    products = Product.objects.all()
    for product in products:
        writer.add_document(
            id=product.id,
            name=product.name,
            price=float(product.price[1:]),
            rating=product.rating,
            image=product.image,
            link=product.link,
            store = product.store.lower()
        )
    writer.commit()