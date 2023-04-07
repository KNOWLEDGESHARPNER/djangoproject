from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from .signals import order_created
from store.models import Customer, Order, OrderItem, Product, Collection, Review,Cart,Cartitem

class CollectionSerializer(serializers.ModelSerializer):
   class Meta:
       model=Collection
       fields=['id','title','products_count']
       
   products_count=serializers.SerializerMethodField(method_name='calculate_products_count')
   
   def calculate_products_count(self,collection:Collection):
    return collection.product.count()

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['id','title','unit_price']
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['id','title','slug','description','unit_price','price_with_tax','inventory','collection']
        # fields='__all__'
    # id=serializers.IntegerField()
    # title=serializers.CharField(max_length=255)
    # price=serializers.DecimalField(max_digits=6,decimal_places=2,source='unit_price')
    price_with_tax=serializers.SerializerMethodField(method_name='calculate_tax')
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(),
    #     view_name='collection-detail'
    # )
    
    
    def calculate_tax(self,product:Product):
        return product.unit_price*Decimal(1.1)
    
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Review
        fields=['id','name','description','date']
        
    def create(self, validated_data):
        product_id=self.context['product_id']
        return Review.objects.create(product_id=product_id,**validated_data)
        
        
class CartItemSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer()
    total_price=serializers.SerializerMethodField()
    
    def get_total_price(self,cart_item:Cartitem):
        return cart_item.quantity * cart_item.product.unit_price
    class Meta:
        model=Cartitem
        fields=['id','product','quantity','total_price']

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id=serializers.IntegerField()
    class Meta:
        model=Cartitem
        fields=['id','product_id','quantity']
    
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No Product with given Id was found ')
        
        return value 
    
    def save(self, **kwargs):
        cart_id=self.context['cart_id']
        product_id=self.validated_data['product_id']
        quantity =self.validated_data['quantity']
        try:
            cart_item=Cartitem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity+=quantity
            cart_item.save()
            self.instance=cart_item
        except Cartitem.DoesNotExist:
            self.instance= Cartitem.objects.create(cart_id=cart_id,**self.validated_data)
        return self.instance
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cartitem
        fields=['quantity']
class CartSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    items=CartItemSerializer(many=True,read_only=True)
    total_price=serializers.SerializerMethodField()
    
    def get_total_price(self,cart):
        return sum([item.quantity*item.product.unit_price for item in cart.items.all()])
    class Meta:
        model=Cart
        fields=['id','items','total_price','total_price']
        

class CustomerSerializer(serializers.ModelSerializer):
    user_id=serializers.IntegerField(read_only=True)
    class Meta:
        model=Customer
        fields=['id','user_id','phone','birth_date','membership']
        
class OrderItemSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer()
    class Meta:
        model=OrderItem
        fields=['id','product','unit_price','quantity']
        
class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True)
    class Meta:
        model=Order
        fields=['id','customer','placed_at','payment_status','items']
        
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=['payment_status']
class CreateOrderSerializer(serializers.Serializer):
    cart_id=serializers.UUIDField()
    
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id):
            raise serializers.ValidationError('No cart with the given id found.')  
        if Cartitem.objects.filter(cart_id=cart_id).count()==0:
            raise serializers.ValidationError('The cart is empty')
        return cart_id
    
    def save(self, **kwargs):
        cart_id=self.validated_data['cart_id']
        
        with transaction.atomic():
            customer=Customer.objects.get(user_id=self.context['user_id'])  
            order=Order.objects.create(customer=customer)
            
            cart_items=Cartitem.objects \
                                    .select_related('product') \
                                    .filter(cart_id=cart_id)
            
            order_items=[
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=cart_id).delete()
            
            order_created.send_robust(self.__class__,order=order)
            
            return order
            