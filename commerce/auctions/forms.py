from django import forms
from .models import Listing, Category

class CreateForm(forms.ModelForm):
    # item_category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)  # If you want this field to be optional

    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'url', 'item_category']