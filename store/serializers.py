from decimal import Decimal
from rest_framework import serializers

from store.models import Product, Collection, Review,Cart,Cartitem

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