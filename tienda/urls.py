from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.catalogue, name = 'catalogo'),
    path('cart/', views.cart, name='ver_carrito'),
    path('cart/add/<int:game_id>/', views.add_to_cart, name='agregar_al_carrito'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='eliminar_del_carrito'),

    path('checkout/', views.checkout, name='procesar_checkout'),
    
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('historial/', views.transsactions, name='historial_transacciones'),
]