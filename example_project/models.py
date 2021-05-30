from django.db import models
from django.utils import timezone
from django.conf import settings
from django_cropper_image.fields import ImageCropperField

class Images(models.Model):
	image = ImageCropperField(upload_to='image')
	# image = models.FileField(upload_to='documents/')
	comment = models.CharField(max_length=255)