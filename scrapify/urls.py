from django.contrib import admin
from django.urls import path
from user import views as user_views
from product import views as product_views

urlpatterns = [
    path('',product_views.get_all_products, name= 'get_all_products'),
    path('admin/', admin.site.urls),
    path('login/',user_views.login_view, name = 'login'),
    path('logout/',user_views.logout_view, name = 'logout'),
    path('signup/',user_views.sign_up, name = 'sign_up'),
    path('scraper/<str:store>/',product_views.scraper, name = 'scraper'),
]
