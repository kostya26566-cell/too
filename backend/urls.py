from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('profile/', views.ProfileView.as_view()),
    path('categories/', views.CategoryListView.as_view()),
    path('products/', views.ProductListView.as_view()),
    path('products/<int:pk>/', views.ProductDetailView.as_view()),
    path('shops/', views.ShopListView.as_view()),
    path('shop/profile/', views.ShopProfileView.as_view()),
    path('contacts/', views.ContactListCreateView.as_view()),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view()),
    path('cart/', views.CartView.as_view()),
    path('orders/', views.OrderListView.as_view()),
    path('orders/<int:pk>/', views.OrderDetailView.as_view()),
]