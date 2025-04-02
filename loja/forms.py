from django import forms
from .models import Comprovante


class ComprovanteForm(forms.ModelForm):
    class Meta:
        model = Comprovante
        fields = ['arquivo']
        labels = {
            'arquivo': 'Comprovante de Pagamento'
        }
        help_text = {
            'arquivo': 'Aceita imagens (JPG, PNG, GIF) e PDFs'
        }
