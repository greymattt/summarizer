from django import forms

class Linker(forms.Form):
    link = forms.CharField(label="link", max_length=200)
