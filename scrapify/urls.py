from django.contrib import admin
from django.urls import path
from user import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',user_views.login_view, name = 'login')
]
