from django import forms

from .models import Review, UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("avatar", "bio")
        widgets = {
            "avatar": forms.URLInput(attrs={"placeholder": "https://..."}),
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Cuéntanos sobre ti"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
        labels = {"rating": "Calificación", "comment": "Reseña"}
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
            "comment": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if not 1 <= rating <= 10:
            raise forms.ValidationError("La calificación debe estar entre 1 y 10.")
        return rating
