from django.urls import path

from . import views

app_name = 'recomendaciones'

urlpatterns = [
    path('', views.recomendaciones_page, name='recomendaciones_page'),
    path('api/', views.RecomendacionesView.as_view(), name='recomendaciones_api'),
    path('preferencias/', views.update_preferences, name='update_preferences'),
]
