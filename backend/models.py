from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

# Модель пользователя
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_shop = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email

# Модель магазина
class Shop(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
    state = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

# Модель категории
class Category(models.Model):
    name = models.CharField(max_length=40, unique=True)
    
    def __str__(self):
        return self.name

# Модель товара
class Product(models.Model):
    name = models.CharField(max_length=80)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=True)
    
    def __str__(self):
        return self.name

# Модель информации о товаре
class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_infos')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_infos')
    name = models.CharField(max_length=80)
    model = models.CharField(max_length=80, blank=True)
    external_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        unique_together = ('product', 'shop', 'external_id')

# Модель параметра
class Parameter(models.Model):
    name = models.CharField(max_length=40, unique=True)
    
    def __str__(self):
        return self.name

# Модель параметра товара
class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='product_parameters')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='product_parameters')
    value = models.CharField(max_length=100)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter')
        ]

# Модель контакта
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    house = models.CharField(max_length=15)
    structure = models.CharField(max_length=15, blank=True)
    building = models.CharField(max_length=15, blank=True)
    apartment = models.CharField(max_length=15, blank=True)
    phone = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.city}, {self.street} {self.house}"

# Модель заказа
class Order(models.Model):
    STATUS_CHOICES = [
        ('basket', 'Статус корзины'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True, related_name='orders')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='basket')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Заказ #{self.id}"

# Модель товара в заказе
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.product_info.name} x{self.quantity}"

# Модель токена подтверждения email
class ConfirmEmailToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='confirm_email_tokens')
    key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.key:
            import secrets
            self.key = secrets.token_urlsafe(30)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Токен для {self.user.email}"