=====================
django-cropper-image
=====================


django-cropper-image is an app for client side cropping and compressing uploaded images via Django's app using with help cropper.js `cropperjs
<https://github.com/fengyuanchen/cropperjs>`_.
github link `django-cropper-image
<https://github.com/aneesh2usman/django_cropper_image>`_.

Screenshot:

.. image:: https://github.com/aneesh2usman/django_cropper_image/blob/main/doc/Screenshot.png


django-cropper-image is very usefull image upload with a specific size for your templates. it is more userfriendly no need add more field for cropping data storage in your db.
django-cropper-image is keep both cropped image and orginal image and also setting custom configuration as you need like aspect ratio (3:4,16:9) vise versa. and you can set minimum and maximum crop width and height.
it can also set compressing of image.


Installation
============

#. Install django-cropper-image using ``pip``::

    pip install django-cropper-image


    INSTALLED_APPS = [
        ...
        'django_cropper_image',
    ]


Configuration
=============

Add an ``ImageCropperField`` to the model that images you want to crop.you don't worried about if form error occure the image is remove 

models 
======

#. ``Models.py``::

    from django.db import models
    from django_cropper_image.fields import ImageCropperField

    class Images(models.Model):
        image = ImageCropperField(upload_to='image',max_length=255)

forms
=====

#. ``forms.py``::

    from django import forms
    from django.forms import ModelForm
    from .models import Images

    class ImageForm(ModelForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Form configuration is optional. You can change the default.
            self.fields['image'].widget.attrs.update({
                'data-aspectratio_w':16, #aspect ratio of width (Default : 1)
                'data-aspectratio_h':9, #aspect ratio of height (Default : 1)
                'data-minCropWidth' : 300, #minimum crop width 
                'data-minCropHeight' : 300, #minimum crop height 
                'data-maxCropWidth' : 600, #maximum crop width
                'data-maxCropHeight' :600, #maximum crop height
                'data-cropRestrict':"true", #minimum and maximum  work only when cropRestrict true
                'data-mincontainerwidth' : 300, #minimum width of image container
                'data-mincontainerheight' : 300,#minimum height of image container
                'data-filesize' : 0.5, #. 1 mb 2mb if the file size reach config file size it will be compress
                'data-fileresolution' : 0.7, #.0.7 medium resolution
                'data-fillcolor' : '#fff', #color of the cropped image background
                'data-maxmainimagewidth' : 2000, #uploaded image maximum width height take accordingily
                'data-compress':"true", # compress yes:No (Default : true)
                'data-orginal_extension':"false", # (Default : false)  if .png no chnage in png file otherwise convert jpg


            })
        
        class Meta:
            model 	= Images
            fields 	= "__all__"
        def clean(self, *args, **kwargs):
            self.cleaned_data = super().clean(*args, **kwargs)

views
=====

#. ``views.py``::

    from django.shortcuts import render
    from django.http import HttpResponse,HttpResponseRedirect
    from django.views import View
    from django.urls import reverse
    from .forms import ImageForm
    from .models import Images
    from django.conf import settings
    class ImageView(View):
        template_dir = "example_project/"
        def get(self, request, *args, **kwargs):
            if 'id' in kwargs and kwargs['id']:
                context={}
                instance =  Images.objects.filter(pk =kwargs['id'] ).first()
                form = ImageForm(instance =instance)
                context['form'] =form
                context['form_media'] =form.media
            elif 'delete_id' in kwargs and kwargs['delete_id']:
                instance =  Images.objects.filter(pk =kwargs['delete_id'] ).delete()
                return HttpResponseRedirect(reverse('image_add')) 
                
            else :
                context ={}
                form = ImageForm()
                context['form'] =form
                context['form_media'] =form.media
            #Send to the render view page
            return render(request, self.template_dir+'home.html',context)
        def post(self, request, *args, **kwargs):
            
            context ={}
            if 'id' in kwargs and kwargs['id']:
                instance =  Images.objects.filter(pk =kwargs['id'] ).first()
                form = ImageForm(request.POST or None,request.FILES or None,instance =instance)
                if request.POST and form.is_valid():
                    form.save()
                    
                    return HttpResponseRedirect(reverse('image_edit',kwargs={'id':kwargs['id']})) 
            else :

                form = ImageForm(request.POST or None,request.FILES or None)
                if request.POST and form.is_valid():
                    form.save()
                    return HttpResponseRedirect(reverse('image_add')) 
            context['form'] =form
            context['form_media'] =form.media
            
            #Send to the render view page
            return render(request, self.template_dir+'home.html',context)

templates
========= 

#. templates.html::

    {% load static %}
    {% load i18n %}

    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="Django image cropper.">
    <meta name="author" content="Aneesh Usman">
    {% block stylesheet %}
    {% if form_media.css %}
        {{ form_media.css }}
    {% endif %}
    {% endblock %}
    <title>Django Image Cropper</title>
    </head>
    <body>
    
    <form method="{{form.method|default:'POST'}}" enctype="multipart/form-data" class="{{form.class}} m-form m-form--fit m-form--label-align-right" action="{{form.action|default:request.path}}" novalidate>
        {% csrf_token %}
        {{ form }}
        <input type="submit" value="Submit">
    </form>


    <!-- Scripts -->
    
    <script src="/static/example_project/js/jquery-3.4.1.slim.min.js" crossorigin="anonymous"></script>
    <script src="/static/example_project/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script>
    {% block javascript %}
            {% if form_media.js %}
            {{ form_media.js }}
            {% endif %}
        {% endblock %}

    </body>
    </html>






    

