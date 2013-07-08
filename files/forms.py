from django import forms

class FileForm(forms.Form):
    target_type = forms.CharField(widget=forms.HiddenInput)
    target_id   = forms.CharField(widget=forms.HiddenInput)
    filedata    = forms.FileField(label='Upload file')

class ImageForm(forms.Form):
    target_type = forms.CharField(widget=forms.HiddenInput)
    target_id   = forms.CharField(widget=forms.HiddenInput)
    filedata    = forms.FileField(label='Upload image')
