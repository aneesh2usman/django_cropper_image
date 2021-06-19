from django.forms import widgets
from django.conf import settings
from hashlib import md5
import time
DEFAULT_EXT ='jpg'
class CropperConstant(object):
	def __init__(self):
		self.assign()
	def assign(self):
		self.cropper_data= {
			'full':'',
			'cropped':'',
			'image_url': '',
			'x': '',
			'y': '',
			'h' :'',
			'w': '',
			'r': '',
			'full_img': '',
			'full_image_url':'',
			'old_file_path':'',
			'change':1,
			'ext':DEFAULT_EXT,
			'filename':'dummy',
			'full_save':True,
			'full_ext':DEFAULT_EXT,
			'orginal_ext':False,
			'old_file_path_save':False,

		}
		return self.cropper_data
	def reset(self):
		return self.assign()
	def set(self,name="",data ={}):
		self.cropper_data.update(
			{
				'change':1,
				'x': data[f'{name}_x'],
				'y': data[f'{name}_y'],
				'w': data[f'{name}_w'],
				'h': data[f'{name}_h'],
				'r': data[f'{name}_r'],
				'full_img':data[f'{name}_full_img'],
				'change':data[f'{name}_change'],
				'ext':'jpg',
				'full_save':True,
				'timestamp':time.time(),
				'old_file_path':data[f'{name}_old_file_path'],
				
			
			}
		)
		
		if f'{name}_full' in data:
			self.cropper_data.update(
				{
				   'full':data[f'{name}_full'],                   
				}
			)
		if f'{name}_cropped' in data:
			self.cropper_data.update(
				{
				   'cropped':data[f'{name}_cropped'],
				}
			)
		return self.cropper_data
	def update(self,key=None,value=None):
		self.cropper_data.update({key:value})

	def get(self):
		return self.cropper_data
class FileInputCropper(widgets.Input):
	class Media:
		js = ('django_cropper_image/js/cropper.min.js','django_cropper_image/js/image_cropper.min.js',)
		css = {'all':('django_cropper_image/css/cropper.min.css','django_cropper_image/css/image_cropper.css',)}
	template_name = 'django_cropper_image/image_cropper_input.html'
	
	input_type = 'file' 
	def __init__(self, attrs=None):
		super().__init__(attrs)
		self.cropperconstobj = CropperConstant()
		self.cropper_data = self.cropperconstobj.cropper_data
		
		
	def get_context(self, name, value, attrs):
		if value and isinstance(value, str):
			self.cropper_data.update({'full':''})
			self.cropper_data = self.cropperconstobj.reset()
		elif not value:
			self.cropper_data.update({'full':''})
			self.cropper_data = self.cropperconstobj.reset()
		self.get_full_image(value)
		self.get_cropped_image_coordinates(value)
		self.context = super().get_context(name, value, attrs)
		if self.attrs.get('data-orginal_extension'):
			self.cropper_data.update({'orginal_ext': True})
		self.cropper_data.update({'image_url': ''})
		self.cropper_data.update({'change': 1})
		self.cropper_data.update({'full_save':True})
		if value and  hasattr(value, 'name'):
			self.cropper_data.update({'image_url': value.name})
		self.context['widget'].update({
			'name':name,
			'image_obj':value
		})
		self.context['widget'].update({**self.cropper_data})
		self.generate_filename()
		return self.context
	def get_full_image(self, value):
		full_image_data =''
		if value:
			
			try:
				imagenamessplits = value.split("_crop")
				self.cropper_data.update({'old_file_path': value})
				ext = value.split(".")[-1]
				

				full_image_data = imagenamessplits[0] + '.' + ext

				if  not self.cropper_data['full']:
					self.cropper_data.update(
						{
						'full':settings.MEDIA_URL+full_image_data,                   
						}
					)
				else:
					pass
			except:
				full_image_data = value
			self.cropper_data.update({'full_image_url': full_image_data})
	def get_cropped_image_coordinates(self, value):
		if value:
			try:
				Paramsdict = {}
				params =  value.split(".")[0]
				params = params.replace("--d--", ".")
				crop_split = params.split("_crop_")
				paramssplits = crop_split[1].split("_")
				self.cropper_data.update({'x': paramssplits[0],'y': paramssplits[1],'w': paramssplits[2],'h': paramssplits[3],'r': paramssplits[4],})
			except Exception as e:
				pass
	def generate_filename(self):
		prefix = md5(str(time.localtime()).encode('utf-8')).hexdigest()
		self.cropper_data.update({
			'filename_prefix':f"{prefix}"
		})
		
	def value_from_datadict(self, data, files, name):
		upload = super().value_from_datadict(data, files, name)
		self.cropper_data = self.cropperconstobj.set(name,data)
		self.generate_filename()
		#upload.cropper_data = self.cropper_data
		return self.cropperconstobj

	

