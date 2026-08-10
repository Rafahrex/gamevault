from django import forms

from .models import UserPreference


class PreferenceForm(forms.ModelForm):
    """Formulario para que el usuario personalice sus gustos desde el cliente.

    Los géneros favoritos y el precio máximo que el usuario guarda aquí son
    exactamente los datos que consume el pipeline funcional (filter -> map ->
    sorted -> top-N) de recomendaciones/pipeline.py.
    """

    class Meta:
        model = UserPreference
        fields = ['favorite_genres', 'max_price']
        widgets = {
            'favorite_genres': forms.CheckboxSelectMultiple,
            'max_price': forms.NumberInput(
                attrs={
                    'step': '0.01',
                    'min': '0',
                    'placeholder': 'Ej: 59.99',
                    'style': (
                        'width:180px; background:#0e141d; color:#c6d4df;'
                        ' border:1px solid #2a475e; padding:8px;'
                        ' border-radius:2px;'
                    ),
                }
            ),
        }
        labels = {
            'favorite_genres': 'Géneros favoritos',
            'max_price': 'Precio máximo (USD)',
        }
