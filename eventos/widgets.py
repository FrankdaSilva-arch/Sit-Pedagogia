from django import forms

class CoordenadorAutocompleteWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        print("[LOG] CoordenadorAutocompleteWidget inicializado")
        super().__init__(*args, **kwargs)
    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/awesomplete/1.1.5/awesomplete.min.js',
            'eventos/js/coordenador_autocomplete.js',
        )
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/awesomplete/1.1.5/awesomplete.min.css',)
        } 