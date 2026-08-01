from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('profile/', views.ProfileView.as_view()),
    path('confirm-email/', views.ConfirmEmailView.as_view()),
    path('password-reset/', views.PasswordResetView.as_view()),
    
    path('categories/', views.CategoryListView.as_view()),
    path('products/', views.ProductListView.as_view()),
    path('products/<int:pk>/', views.ProductDetailView.as_view()),
    
    path('shops/', views.ShopListView.as_view()),
    path('shop/profile/', views.ShopProfileView.as_view()),
    
    path('partner/update/', views.PartnerUpdateView.as_view()),
    path('partner/state/', views.PartnerStateView.as_view()),
    path('partner/orders/', views.PartnerOrdersView.as_view()),
    
    path('contacts/', views.ContactListCreateView.as_view()),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view()),
    
    path('cart/', views.CartView.as_view()),
    path('cart/item/<int:pk>/', views.CartItemView.as_view()),
    path('cart/checkout/', views.CartCheckoutView.as_view()),
    
    path('orders/', views.OrderListView.as_view()),
    path('orders/<int:pk>/', views.OrderDetailView.as_view()),
    path('orders/<int:order_id>/status/', views.OrderStatusUpdateView.as_view()),
]