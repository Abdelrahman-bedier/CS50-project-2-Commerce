from django.urls import path

from . import views

app_name = 'auctions'

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/<int:id>", views.listing, name="listing"),
    path('watchlist', views.watchlist, name='watchlist'),
    path('category', views.category, name='category'),
    path('category/<str:category>', views.specific_category, name='specific_category')
]
