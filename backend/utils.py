import yaml
import requests
from django.db import transaction
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

def import_products_from_yaml(url, user):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = yaml.safe_load(response.content)
        shop = Shop.objects.get(user=user)
        
        with transaction.atomic():
            for cat in data.get('categories', []):
                Category.objects.update_or_create(
                    id=cat['id'],
                    defaults={'name': cat['name']}
                )
            
            for good in data.get('goods', []):
                product, _ = Product.objects.update_or_create(
                    name=good['name'],
                    defaults={'category': Category.objects.get(id=good['category'])}
                )
                pi, _ = ProductInfo.objects.update_or_create(
                    product=product,
                    shop=shop,
                    external_id=good['id'],
                    defaults={
                        'name': good['name'],
                        'model': good.get('model', ''),
                        'quantity': good['quantity'],
                        'price': good['price'],
                        'price_rrc': good['price_rrc'],
                    }
                )
                for param in good.get('parameters', []):
                    p, _ = Parameter.objects.get_or_create(name=param['name'])
                    ProductParameter.objects.update_or_create(
                        product_info=pi,
                        parameter=p,
                        defaults={'value': param['value']}
                    )
        return True, "Импорт выполнен"
    except Exception as e:
        return False, str(e)