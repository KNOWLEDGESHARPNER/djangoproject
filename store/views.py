from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import CreateModelMixin,DestroyModelMixin,RetrieveModelMixin,UpdateModelMixin
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.filters import SearchFilter,OrderingFilter

from store.permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermission

from .pagination import DefaultPagination
from .filters import ProductFilter
from .models import Cart,Cartitem, Customer, Order, OrderItem, Product,Collection, Review
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductSerializer,CollectionSerializer, ReviewSerializer, UpdateCartItemSerializer, UpdateOrderSerializer

class ProductViewSet(ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class=ProductFilter
    pagination_class=DefaultPagination
    permission_classes=[IsAdminOrReadOnly]
    search_fields=['title','description']
    ordering_fields=['unit_price','last_update']
    
    # def get_queryset(self):
    #     collection_id=self.request.query_params.get('collection_id')
    #     if collection_id is not None:
    #         queryset=queryset.filter(collection_id=collection_id)
    #     return queryset
    
    def get_serializer_context(self):
        return {"request":self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response({'error':'product can not be deleted it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)     
        
        return super().destroy(request, *args, **kwargs)    
       
       
        
        
    
    # def delete(self,request,pk):
    #     product=get_object_or_404(Product,pk=pk)

# class ProductList(ListCreateAPIView):
    
#     # def get(self,request):
#     #     queryset=Product.objects.select_related('collection').all()
#     #     serializer=ProductSerializer(queryset,many=True,context={'request':request})
#     #     return Response(serializer.data)
#     # def post(self,request):
#     #     serializer=ProductSerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data,status=status.HTTP_201_CREATED)



# class ProductDetails(RetrieveUpdateDestroyAPIView):
    
    
#     # def get(self,request,id):
#     #     product=get_object_or_404(Product,pk=id)
#     #     serializer=ProductSerializer(product)
#     #     return Response(serializer.data)
#     # def put(self,request,id):
#     #     product=get_object_or_404(Product,pk=id)
#     #     serializer=ProductSerializer(product,data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data)
    
class CollectionVeiwSet(ModelViewSet):
    queryset=Collection.objects.all()
    serializer_class=CollectionSerializer
    permission_classes=[IsAdminOrReadOnly]
    
    def destroy(self, request, *args, **kwargs):
        if Collection.objects.filter(product=kwargs['pk']).count()>0:
            return Response({'error':'product can not be deleted it includes one or more products'},status=status.HTTP_405_METHOD_NOT_ALLOWED)     
        
        return super().destroy(request, *args, **kwargs)
        
    
    

# class CollectionList(ListCreateAPIView):
    
# @api_view(['GET','POST'])
# def collection_list(request):
#     if request.method=='GET':
#         queryset=Collection.objects.all()
#         serializer=CollectionSerializer(queryset,many=True,context={'request':request})
#         return Response(serializer.data)
    
#     elif request.method=='POST':
#         serializer=CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data,status=status.HTTP_201_CREATED)   



# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset=Collection.objects.all()
#     serializer_class=CollectionSerializer
    
        
        
# @api_view(['GET','PUT','DELETE'])
# def collection_detail(request,pk):
#     collection=get_object_or_404(Collection,pk=pk)
#     if request.method=='GET':
#         serializer=CollectionSerializer(collection)
#         return Response(serializer.data)
#     elif request.method=='PUT':
#         serializer=ProductSerializer(collection,data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method=='DELETE':
#         if collection.product.count()>0:
#             return Response({'error':'product can not be deleted it includes one or more products'},status=status.HTTP_405_METHOD_NOT_ALLOWED)     
#         else:
#             collection.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewViewSet(ModelViewSet):
    # queryset=Review.objects.all()
    serializer_class=ReviewSerializer
    
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}
    
class CartViewSet(CreateModelMixin,
                  DestroyModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet):
    queryset=Cart.objects.prefetch_related('items__product').all()
    serializer_class=CartSerializer
    
    
class CartItemViewSet(ModelViewSet):
    # queryset=Cartitem.objects.select_related('product')
    # serializer_class=CartItemSerializer
    http_method_names=['get','post','patch','delete']
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}
    
    
    def get_queryset(self):
        return Cartitem.objects.filter(cart_id=self.kwargs['cart_pk']) .select_related('product')
    
    def get_serializer_class(self):
        if self.request.method=='POST':
            return AddCartItemSerializer
        elif self.request.method=='PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
class CustomerViewSet(ModelViewSet):
    
    queryset=Customer.objects.all()
    serializer_class=CustomerSerializer
    permission_classes=[IsAdminUser]
    
    # def get_permissions(self):
    #     if self.request.method=='GET':
    #         return [AllowAny()]
    #     return [IsAuthenticated()]
    
    @action(detail=True,permission_classes=[ViewCustomerHistoryPermission])
    def history(self,request,pk):
        return Response('ok')
    
    @action(detail=False,methods=['GET','PUT'],permission_classes=[IsAuthenticated])
    def me(self,request):
        customer=Customer.objects.get(user_id=request.user.id)
        
        if request.method=='GET':
            serializer=CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method=='PUT':
            serializer=CustomerSerializer(customer,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
class OrderViewSet(ModelViewSet):
    # queryset=Order.objects.all()
    # serializer_class=OrderSerializer
    http_method_names=['get','post','patch','delete','head','options']
    permission_classes=[IsAuthenticated]
    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        serializer=CreateOrderSerializer(data=request.data,
                                         context={'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order=serializer.save()
        serializer=OrderSerializer(order)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        if self.request.method=='POST':
            return CreateOrderSerializer
        elif self.request.method=='PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_queryset(self):
        user=self.request.user
        if user.is_staff:
            return Order.objects.all()
        
        customer_id=Customer.objects.only(
            'id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)
    
   
    
    