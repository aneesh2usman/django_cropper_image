from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'License :: OSI Approved :: MIT License',
  "Environment :: Web Environment",
  "Framework :: Django",
  "Framework :: Django :: 2.0",
  "Framework :: Django :: 2.1",
  "Framework :: Django :: 2.1",
  "Intended Audience :: Developers",
  "Operating System :: OS Independent",
  "Programming Language :: Python",
  "Programming Language :: Python",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.6",
  "Programming Language :: Python :: 3.7",
  "Programming Language :: Python :: 3.8",
  "Topic :: Software Development :: Libraries :: Python Modules",
]
 
setup(
  name='django-cropper-image',
  version='1.0.4',
  description='django-cropper-image is an app for client side cropping and compressing uploaded images via Django 2.*',
  # long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  long_description=open('README.rst').read(),
  url='https://github.com/aneesh2usman/django_cropper_image',  
  author='aneesh usman',
  author_email='aneeshplusone@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  include_package_data=True,
  keywords='cropper image', 
  packages=find_packages(),
  python_requires=">=3.6",
  install_requires=[''] 
)
