from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django import forms
import magic
from django.conf import settings
import base64
from .widgets import FileInputCropper
from django.utils.translation import gettext_lazy as _, ngettext_lazy
from django import VERSION
from itertools import chain
from django.db import models
import os
from django.core.files.base import ContentFile
import datetime
import posixpath
from django.core import checks

'''
Model field 
'''
class ImageCropperField(models.Field):
	def __init__(self, verbose_name=None, name=None, upload_to='', storage=None,extentions=['.jpg', '.jpeg', '.png'],
				
				**kwargs):
		self._primary_key_set_explicitly = 'primary_key' in kwargs
		self.storage = storage or default_storage
		self.upload_to = upload_to
		self.extentions = extentions
		self.generated_name =""
		kwargs.setdefault('max_length', 100)
		super().__init__(verbose_name, name, **kwargs)
	def check(self, **kwargs):
		return [
			*super().check(**kwargs),
			*self._check_primary_key(),
			*self._check_upload_to(),
		]

	def _check_primary_key(self):
		if self._primary_key_set_explicitly:
			return [
				checks.Error(
					"'primary_key' is not a valid argument for a %s." % self.__class__.__name__,
					obj=self,
					id='fields.E201',
				)
			]
		else:
			return []

	def _check_upload_to(self):
		if isinstance(self.upload_to, str) and self.upload_to.startswith('/'):
			return [
				checks.Error(
					"%s's 'upload_to' argument must be a relative path, not an "
					"absolute path." % self.__class__.__name__,
					obj=self,
					id='fields.E202',
					hint='Remove the leading slash.',
				)
			]
		else:
			return []
	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		if kwargs.get("max_length") == 100:
			del kwargs["max_length"]
		kwargs['upload_to'] = self.upload_to
		if self.storage is not default_storage:
			kwargs['storage'] = self.storage
		return name, path, args, kwargs

	def get_internal_type(self):
		return "FileField"

	def get_prep_value(self, value):
		value = super().get_prep_value(value)
		# Need to convert File objects provided via a form to string for database insertion
		if value is None:
			return None
		return str(value)

	def generate_filename(self, instance, filename):
		"""
		Apply (if callable) or prepend (if a string) upload_to to the filename,
		then delegate further processing of the name to the storage backend.
		Until the storage layer, all file paths are expected to be Unix style
		(with forward slashes).
		"""
		if self.b64data and 'filename_prefix' in self.b64data:
			if not callable(self.upload_to):
				self.generated_name = self.upload_to+self.b64data["filename_prefix"]
			else:
				self.generated_name = self.b64data["filename_prefix"]
		ext = self.get_img_extension()
		if hasattr(self,'flag'):
			if self.flag == "crop":
				self.delete_old_file()
				self.generated_name = self.set_generated_cropped_name(self.generated_name)
		filename = '{}.{}'.format(self.generated_name, ext)
		if callable(self.upload_to):
			filename = self.upload_to(instance, filename)
		else:
			dirname = datetime.datetime.now().strftime(self.upload_to)
			filename = posixpath.join(dirname, filename)
		return self.storage.generate_filename(filename)
	def delete_old_all_file(self):
		if 'old_file_path' in self.b64data and self.b64data['old_file_path']:		
			try:
				#remove old crop image
				self.delete_old_full_img()
				self.delete_old_cropped_img()
			except Exception as e:
				pass
			pass
	def delete_old_file(self):
		if self.b64data and 'full_save' in self.b64data and self.b64data['full_save'] ==False:
			if 'old_file_path' in self.b64data and self.b64data['old_file_path']:
				self.delete_old_cropped_img(set_name =True)
		elif self.b64data and 'full_save' in self.b64data and self.b64data['full_save'] ==True:
			if 'old_file_path' in self.b64data and self.b64data['old_file_path']:
				self.delete_old_full_img()
				self.delete_old_cropped_img()
	def delete_old_full_img(self):
		try:
			#remove old crop image
			old_image  = self.b64data['old_file_path'].split("/")[-1]
			crop_split = old_image.split("_crop_")
			crop_split[1].split(".")[-1]
			main_image = self.upload_to+'/'+crop_split[0]+'.'+crop_split[1].split(".")[-1]
			main_image_path =settings.MEDIA_ROOT+'/'+main_image
			self.storage.delete(main_image_path)
		except Exception as e:
			pass
	def delete_old_cropped_img(self,set_name=False):
		if set_name and self.b64data['full']:
			filename2 = self.b64data['full'].split("/")[-1]
			self.generated_name = filename2.split(".")[0]
		try:
			
			crop_image= settings.MEDIA_ROOT+'/'+self.b64data['old_file_path']
			self.storage.delete(crop_image)
		except Exception as e:
			pass
	def full_save_false(self):
		filename =""
		if self.b64data and 'full_save' in self.b64data and self.b64data['full_save'] ==False:
			if 'full' in self.b64data and self.b64data['full']:
				
				filename = self.b64data['full'].split("/")[-1]
				ext = filename.split(".")[-1]
				filename = filename.split(".")[0]
				
				self.generated_name = self.set_generated_cropped_name(filename)
				filename = '{}/{}.{}'.format(self.upload_to,self.generated_name, ext)

		if (
			('full' in self.b64data and not self.b64data['full'])
			and
			('cropped' in self.b64data and not self.b64data['cropped'])
		):	
			self.delete_old_all_file()
		return filename
	def set_generated_cropped_name(self,filename):
		name =""
		x = self.b64data['x']
		y = self.b64data['y']
		w = self.b64data['w']
		h = self.b64data['h']
		r = self.b64data['r']
		name = filename+'_crop_' + x.replace('.', '--d--') + '_'+ y.replace('.', '--d--') +'_'+ w.replace('.', '--d--') + '_'+h.replace('.', '--d--') + '_'+r.replace('.', '--d--')  
		return name
	def get_img_extension(self):
		ext = 'jpg'
		if 'ext' in self.b64data and self.b64data['ext']:
			ext =  self.b64data['ext']
		return ext

	def pre_save(self, model_instance, add):
		"""Return field's value just before saving."""
		self.cropperconstobj = getattr(model_instance, self.attname)
		self.b64data = self.cropperconstobj.get()
		if self.b64data and isinstance(self.b64data, str) or self.b64data =='':
			return self.b64data
		cropping_image =False
		self.filepath =''
		if self and self.name and self.b64data:
			if 'delete_only' in self.b64data and self.b64data['delete_only']:
				pass
			else:
				if 'cropped' in self.b64data and self.b64data['cropped']:
					
					#self.existing_image_edit()
					cropped_img = self.b64data['cropped']
					original_img = self.b64data['full']
					x = self.b64data['x']
					y = self.b64data['y']
					w = self.b64data['w']
					h = self.b64data['h']
					r = self.b64data['r']
					try:
						#save orginal 
						self.save_orginal(original_img,model_instance)
						format, imgstr = cropped_img.split(';base64,') 
						data = ContentFile(base64.b64decode(imgstr))
						self.flag = "crop"
						self.save_base64(self.b64data['filename_prefix'], data,model_instance)
						self.flag =""
						cropping_image =True
							
					except ValueError:
						pass
				else:
					filepath = self.full_save_false()
					self.filepath =filepath
		
		self.b64data = setattr(model_instance, self.attname,self.filepath)
		return self.filepath
	def save_orginal(self,data,model_instance):
		if self.b64data['full_save']:
			format, imgstr = data.split(';base64,') 
			
			data = ContentFile(base64.b64decode(imgstr))
			self.save_base64(self.b64data['filename_prefix'], data,model_instance)

	def save_base64(self,name, content,model_instance, save=True):
		name = self.generate_filename(model_instance, name)
		filepath = self.storage.save(name, content)
		
		self.filepath =filepath
	def formfield(self, **kwargs):
		self.formfieldobj =  super().formfield(**{
			'form_class': FileFieldCropper,
			'max_length': self.max_length,
			'fieldobj': self,
			**kwargs,
			
		})        
		return self.formfieldobj
	


'''
Form field 
'''

class FileFieldCropper(forms.FileField):
	default_error_messages = {
		# 'invalid_upload': _(
		# 	_('upload a valid extentions. %(value)s is not one of the valid choices. please upload valid format like %(extentions)s'),
		# ),
		'invalid_upload': _(
			_('You have uploaded an invalid file.  Please upload the file with the following valid format %(extentions)s'),
		),
		'corrupted_upload': _(
			_('upload a valid file or upload file is corrupted'),
		),
		'file_not_found': _(
			_('Image file not found'),
		),
	}   
	widget = FileInputCropper    
	def __init__(self, *, max_length=None, allow_empty_file=False,fieldobj =None,extentions=['.jpg', '.jpeg', '.png'],widget=widget ,**kwargs):        
		self.max_length = max_length
		self.allow_empty_file = allow_empty_file
		self.extra_dict = {}
		self.fieldobj = fieldobj
		self.widget_data = widget
		self.extentions =extentions
		self.storage =  default_storage
		super().__init__(**kwargs)   
	
	def to_python(self, data):
		
		"""
		Check that the file-upload field data contains a valid extentions
		"""
		extract_data = data.get()
		baseb4images = ['full','cropped']
		self.get_extentions()
		for baseb4image in baseb4images:
			if baseb4image in extract_data and extract_data[baseb4image]:
				validate =True
				try:
					format, imgstr = extract_data[baseb4image].split(';base64,') 
					filetype = magic.from_buffer(base64.b64decode(imgstr), mime=True)
				except Exception as e:
					if baseb4image =="full":
						full_image_url =settings.MEDIA_ROOT+extract_data['full'].replace(settings.MEDIA_URL,'/')
						
						if self.storage.exists(full_image_url):
							validate =False
							extract_data['full_save'] =False
				try:		
					if validate:
						mime_data = filetype.split("/")
						if mime_data:
							ext = mime_data[1]
							extension = '.'+ ext.lower()
							if not extension in self.extentions:
								extstr =  self.extentions
								s = ', '
								
								raise ValidationError(
									self.error_messages['invalid_upload'],
									code='invalid_upload',
									params={'value': ext,'extentions':s.join(extstr)},
								)
						else:
							raise ValidationError(
									self.error_messages['corrupted_upload'],
									code='corrupted_upload',
									
								)
				except Exception as e:
					raise ValidationError(
							self.error_messages['corrupted_upload'],
							code='corrupted_upload',
							
						)
			else :
				if extract_data['full_save'] == True and self.required == False:
					return extract_data
				else:
					raise ValidationError(
								self.error_messages['file_not_found'],
								code='file_not_found',
								
							)
		
		return data
	def get_extentions(self):
		return self.extentions