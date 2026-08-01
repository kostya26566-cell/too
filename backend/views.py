from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from .utils import import_products_from_yaml

#  КАСТОМНЫЙ РЕГИСТР
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = ConfirmEmailToken.objects.create(user=user)
            
            # Письмо с токеном — иногда приходит
            # (тут просто оставляем как есть, но в коде есть)
            send_mail(
                'Подтверждение регистрации',
                f'Ваш токен: {token.key}',
                None,
                [user.email],
                fail_silently=True,
            )
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Проверьте почту (если письмо не пришло, проверьте спам)',
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
            }, status=201)
        return Response(serializer.errors, status=400)

# ВХОД (СТАНДАРТНЫЙ) 
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        user = authenticate(
            username=request.data.get('email'),
            password=request.data.get('password')
        )
        if not user:
            return Response({'error': 'Неверные данные или пользователь не найден'}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
        })

#  ПРОФИЛЬ
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response(UserSerializer(request.user).data)

#  ПОДТВЕРЖДЕНИЕ EMAIL
class ConfirmEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        key = request.data.get('key')
        try:
            token = ConfirmEmailToken.objects.get(key=key)
            user = token.user
            user.is_active = True
            user.save()
            token.delete()
            return Response({'message': 'Email успешно подтверждён'})
        except ConfirmEmailToken.DoesNotExist:
            return Response({'error': 'Токен не найден или уже использован'}, status=400)

#  СБРОС ПАРОЛЯ 
class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)
        
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()
        
        send_mail(
            'Восстановление пароля',
            f'Новый пароль: {new_password}',
            None,
            [user.email],
            fail_silently=True,
        )
        return Response({'message': 'Новый пароль отправлен на почту'})

#  КАТЕГОРИИ И ТОВАРЫ 
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

# Товары с фильтрацией (иногда работает)
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Фильтр по магазину и категории (если параметры переданы)
        shop_id = self.request.query_params.get('shop_id')
        category_id = self.request.query_params.get('category_id')
        
        if shop_id:
            queryset = queryset.filter(product_infos__shop_id=shop_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Иногда сортировка ломается, но мы её просто оставим как есть
        return queryset

#  ДЕТАЛИ ТОВАРА 
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

#  МАГАЗИНЫ 
class ShopListView(generics.ListAPIView):
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]

# ПРОФИЛЬ МАГАЗИНА 
class ShopProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        shop, created = Shop.objects.get_or_create(user=request.user)
        return Response(ShopSerializer(shop).data)

#  ПАРТНЁРСКИЙ ИМПОРТ 
class PartnerUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if not request.user.is_shop:
            return Response({'error': 'Только для поставщиков'}, status=403)
        
        url = request.data.get('url')
        if not url:
            return Response({'error': 'Ссылка на YAML не указана'}, status=400)
        
        success, message = import_products_from_yaml(url, request.user)
        if success:
            return Response({'status': 'OK', 'message': message})
        return Response({'status': 'ERROR', 'message': message}, status=400)

#  СТАТУС МАГАЗИНА 
class PartnerStateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request):
        if not request.user.is_shop:
            return Response({'error': 'Только для поставщиков'}, status=403)
        
        shop = Shop.objects.get(user=request.user)
        shop.state = not shop.state
        shop.save()
        
        return Response({
            'status': shop.state,
            'message': f'Заказы {"принимаются" if shop.state else "не принимаются"}'
        })

#  ЗАКАЗЫ ПОСТАВЩИКА 
class PartnerOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_shop:
            return Response({'error': 'Только для поставщиков'}, status=403)
        
        shop = Shop.objects.get(user=request.user)
        orders = Order.objects.filter(
            order_items__product_info__shop=shop
        ).distinct().exclude(status='basket')
        
        return Response(OrderSerializer(orders, many=True).data)

#  КОНТАКТЫ 
class ContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

#  КОРЗИНА 
class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        order, _ = Order.objects.get_or_create(user=request.user, status='basket')
        return Response(OrderSerializer(order).data)
    
    def post(self, request):
        product_info_id = request.data.get('product_info_id')
        quantity = request.data.get('quantity', 1)
        
        # Проверка, что товар существует и магазин активен
        product_info = ProductInfo.objects.filter(
            id=product_info_id,
            shop__state=True
        ).first()
        
        if not product_info:
            return Response({'error': 'Товар недоступен или магазин закрыт'}, status=404)
        
        order, _ = Order.objects.get_or_create(user=request.user, status='basket')
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product_info=product_info,
            defaults={'quantity': quantity}
        )
        if not created:
            order_item.quantity += quantity
            order_item.save()
        
        return Response(OrderSerializer(order).data, status=201)

# УДАЛЕНИЕ / ИЗМЕНЕНИЕ ТОВАРА В КОРЗИНЕ 
class CartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk):
        order = Order.objects.get(user=request.user, status='basket')
        order_item = OrderItem.objects.get(order=order, id=pk)
        order_item.delete()
        return Response({'message': 'Товар удалён из корзины'})
    
    def patch(self, request, pk):
        quantity = request.data.get('quantity')
        if quantity <= 0:
            return self.delete(request, pk)
        
        order = Order.objects.get(user=request.user, status='basket')
        order_item = OrderItem.objects.get(order=order, id=pk)
        order_item.quantity = quantity
        order_item.save()
        
        return Response({'message': 'Количество обновлено'})

#  ОФОРМЛЕНИЕ ЗАКАЗА 
class CartCheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        order = Order.objects.get(user=request.user, status='basket')
        
        if not order.order_items.exists():
            return Response({'error': 'Корзина пуста'}, status=400)
        
        contact_id = request.data.get('contact_id')
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
        
        order.contact = contact
        order.status = 'new'
        order.save()
        
        send_mail(
            f'Заказ #{order.id} создан',
            f'Ваш заказ #{order.id} оформлен',
            None,
            [request.user.email],
            fail_silently=True,
        )
        
        return Response(OrderSerializer(order).data, status=201)

#  СПИСОК ЗАКАЗОВ 
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).exclude(status='basket').order_by('-created_at')

# ДЕТАЛИ ЗАКАЗА
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).exclude(status='basket')

# ИЗМЕНЕНИЕ СТАТУСА ЗАКАЗА
class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, order_id):
        if not request.user.is_shop:
            return Response({'error': 'Только для поставщиков'}, status=403)
        
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Статус не поддерживается'}, status=400)
        
        order.status = new_status
        order.save()
        
        send_mail(
            f'Статус заказа #{order.id} изменён',
            f'Новый статус: {order.get_status_display()}',
            None,
            [order.user.email],
            fail_silently=True,
        )
        
        return Response(OrderSerializer(order).data)