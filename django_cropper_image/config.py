
from django.conf import settings

class CropperSettings(object):
	@property
	def default(self):
		settings_default ={
			'EXCLUDE_CROPPERJS':False,
			'CROPPERJS_STATIC_JS':'django_cropper_image/js/cropper.min.js',
			'CROPPERJS_STATIC_CSS':'django_cropper_image/css/cropper.min.css',
			'CUSTOM_STATIC_JS':'django_cropper_image/js/image_cropper.min.js',
			'CUSTOM_STATIC_CSS':'django_cropper_image/css/image_cropper.css',
			'TEMPLATES':'django_cropper_image/image_cropper_input.html',
		}
		
		return settings_default
	def get(self,name):
		settings_default =None
		try:
			if hasattr(settings, 'DJANGO_CROPPER_IMAGE_SETTINGS'):
				settings_default = settings.DJANGO_CROPPER_IMAGE_SETTINGS.get(name,self.default.get(name))
			else:
				settings_default = self.default.get(name)
		except Exception as e:
			ValueError(f'{name} not found')
		return settings_default
	def __call__(self,name):
		return self.get(name)

