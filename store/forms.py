from django import forms
from store.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model  = Product
        fields = ['name', 'description', 'price', 'stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome do produto',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Descrição do produto',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '0.00',
                'step': '0.01',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '0',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-4 py-2',
            }),
        }
        labels = {
            'name':        'Nome',
            'description': 'Descrição',
            'price':       'Preço (R$)',
            'stock':       'Estoque',
            'image':       'Imagem do produto',
        }