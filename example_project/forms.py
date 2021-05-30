from django import forms
from django.forms import ModelForm
from .models import Images

class ImageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({
            'data-aspectratio_w':16,
			'data-aspectratio_h':9,
			# 'data-minCropWidth' : 300,
			# 'data-minCropHeight' : 300,
			# 'data-maxCropWidth' : 600,
			# 'data-maxCropHeight' :600,
            'data-cropRestrict':"true",
        })
      
    class Meta:
        model 	= Images
        fields 	= "__all__"
    def clean(self, *args, **kwargs):
        self.cleaned_data = super().clean(*args, **kwargs)
