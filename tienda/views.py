from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Game, Genre, Cart, CartItem, Order, OrderItem

from perfiles.models import GameLibrary

def catalogue(request):
    games = Game.objects.all()
    
    query = request.GET.get('query')
    if query:
        games = games.filter(title__icontains=query)
        
    genre_id = request.GET.get('genre')
    if genre_id:
        games = games.filter(genre_id=genre_id)

    genres = Genre.objects.all() if 'Genre' in globals() else []

    context = {
        'games': games,
        'genres': genres,
        'query': query or ''
    }

    return render(request, 'tienda/catalogo.html', context)

def _get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    
    cart_id = request.session.get('cart_id')
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
    return cart

def cart(request):
    cart = _get_cart(request)
    context = {
        'cart': cart,
        'items': cart.items.all(),
        'total': cart.get_total_price()
    }
    return render(request, 'tienda/carrito.html', context)

def add_to_cart(request, game_id):
    cart = _get_cart(request)
    game = get_object_or_404(Game, id=game_id)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, game=game)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('ver_carrito')

def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect('ver_carrito')

@login_required(login_url='login')
def checkout(request):
    cart = _get_cart(request)
    items = cart.items.all()

    if not items.exists():
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('ver_carrito')

    total_spent = sum(item.get_subtotal() for item in items)

    
    order = Order.objects.create(
        user=request.user, 
        total=total_spent,
        status='confirmed'  
    )

    purchased_games = []
    for item in items:
        price_to_charge = item.game.get_final_price() if hasattr(item.game, 'get_final_price') else item.game.price

        OrderItem.objects.create(
            order=order,
            game=item.game,
            quantity=item.quantity,
            unit_price=price_to_charge
        )

        GameLibrary.objects.get_or_create(user=request.user, game=item.game)

        if item.game.stock >= item.quantity:
            item.game.stock -= item.quantity
            item.game.save()

        purchased_games.append(item.game)

    cart.items.all().delete()

    messages.success(request, "¡Compra realizada con éxito! El juego se agregó a tu librería.")
    return redirect('catalogo')


@login_required(login_url='login')
def transsactions(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__game')
    return render(request, 'tienda/historial.html', {'orders': orders})



def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            messages.success(request, "Registration successful!")
            return redirect('catalogo')
    else:
        form = UserCreationForm()
    return render(request, 'tienda/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('catalogo')
    else:
        form = AuthenticationForm()
    return render(request, 'tienda/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('catalogo')


