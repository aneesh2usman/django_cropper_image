from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.views import View
from django.urls import reverse
from .forms import ImageForm
from .models import Images
from django.conf import settings
import builtins
from pprint import pprint

def test_form_view(request):
	return render(request, "example_project/home.html", {'form': {}})

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
				print(form.__dict__)
				return HttpResponseRedirect(reverse('image_edit',kwargs={'id':form.instance.pk})) 
		context['form'] =form
		context['form_media'] =form.media
		
		#Send to the render view page
		return render(request, self.template_dir+'home.html',context)
