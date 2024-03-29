from django.urls import include, path
from . import views
# from rest_framework.routers import DefaultRouter,SimpleRouter
from rest_framework_nested import routers

router=routers.DefaultRouter()
router.register('products',views.ProductViewSet,basename='products')
router.register('collections',views.CollectionVeiwSet)
router.register('carts',views.CartViewSet,basename='carts')
router.register('customers',views.CustomerViewSet)
router.register('orders',views.OrderViewSet,basename='orders')

# router.register('cartitems',views.CartItemViewSet,basename='cartitems')
# router.register('reviews',views.ReviewViewSet)

products_router=routers.NestedDefaultRouter(router,'products',lookup='product')
products_router.register('reviews',views.ReviewViewSet,basename='product-review')
carts_router=routers.NestedDefaultRouter(router,'carts',lookup='cart')
carts_router.register('items',views.CartItemViewSet,basename='cart-items')

urlpatterns = router.urls + products_router.urls+carts_router.urls
# urlpatterns = [
#     path('products/',views.ProductList.as_view()),
#     path('products/<int:pk>',views.ProductDetails.as_view()),
#     path('collections/',views.CollectionList.as_view()),
#     path('collections/<int:pk>',views.CollectionDetail.as_view()),
    
# ]
