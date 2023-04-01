from decimal import Decimal
from rest_framework import serializers

from store.models import Product, Collection

class CollectionSerializer(serializers.ModelSerializer):
   class Meta:
       model=Collection
       fields=['id','title','products_count']
       
   products_count=serializers.SerializerMethodField(method_name='calculate_products_count')
   
   def calculate_products_count(self,collection:Collection):
    return collection.product.count()

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
    
    