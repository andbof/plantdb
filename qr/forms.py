from django import forms
from functions import LAYOUT_LIST, DUPLEX_LIST

LAYOUT_CHOICES = zip(LAYOUT_LIST, LAYOUT_LIST)
DUPLEX_CHOICES = zip(DUPLEX_LIST, DUPLEX_LIST)

class QRForm(forms.Form):
    layout = forms.ChoiceField(choices=LAYOUT_CHOICES, label='Layout')
    duplex = forms.ChoiceField(choices=DUPLEX_CHOICES, label='Duplex')
