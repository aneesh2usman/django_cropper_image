
(function ( $ ) {
 
	$.fn.CropperImage = function( options ) {
			
			var defaults = {
					// These are the defaults.
					aspectratio_w : 1,
					aspectratio_h : 1,
					mincontainerwidth : 300,
					mincontainerheight : 300,
					mincanvasheight : 300,
					mincanvaswidth : 300,
					croprestrict : false,
					mincropwidth : 400,
					mincropheight : 400,
					maxcropwidth : 1200,
					maxcropheight : 1200,
					filesize : 0.5,//.1 mb 2mb if the file size reach config file size it will be compress
					fileresolution : 0.7,//.0.7 medium resolution
					fillcolor : '#fff',
					maxmainimagewidth : 2000,
					compress:true,
					orginal_extension:false,
			}
			let plugin = this;
			plugin.default_ext = 'image/jpeg';
			plugin.settings = {}
			plugin.coords = ["h","w","x","y","r"];
			plugin.img_id = $(plugin).attr('id')
			plugin.delete_image_id = "#" + plugin.img_id.split(/_(.+)/)[1] + "-clear_id"
			plugin.container = document.querySelector('#'+plugin.img_id+'_img-ctr');
			plugin.initiator= {
					Cropper : window.Cropper,
					URL : window.URL || window.webkitURL,
					container_div :$('#'+plugin.img_id+'-img-ctr-div'),
					image : plugin.container.getElementsByTagName('img').item(0),
					actions :document.getElementById(plugin.img_id+'-actions'),
					data_h : $("#" + plugin.img_id+"_h").val(),
					data_w : $("#" + plugin.img_id+"_w").val(),
					data_x : $("#" + plugin.img_id+"_x").val(),
					data_y :$("#" + plugin.img_id + "_y").val(),
					data_r : $("#" + plugin.img_id + "_r").val(),
					full_img_val :$("#" + plugin.img_id + "_full").val(),
					defaultCrop : {},
			}
			plugin.originalImageURL = plugin.initiator.image.src;
			plugin.uploadedImageType = 'image/jpeg';
			plugin.uploadedImageName = 'cropped.jpg';
			plugin.uploadedImageURL;
			plugin.getDefault =function() {
				if(options === null || typeof options === "undefined"){

					options = plugin.data()
				} 
				return plugin.settings = $.extend({}, defaults, options);
			}
			
			plugin.init = function() {
				plugin.getDefault()
				if (plugin.initiator.data_h && plugin.initiator.data_w && plugin.initiator.data_x && plugin.initiator.data_y) {
					plugin.initiator.defaultCrop = { "width": parseFloat(plugin.initiator.data_w), "height": parseFloat(plugin.initiator.data_h),"x" : parseFloat(plugin.initiator.data_x),"y" : parseFloat(plugin.initiator.data_y),"rotate" : parseFloat(plugin.initiator.data_r)};
				} 
				plugin.crop_options =  {
					data :plugin.initiator.defaultCrop,
					zoomable : true,
					aspectRatio: parseInt(plugin.settings.aspectratio_w) / parseInt(plugin.settings.aspectratio_h),
					preview: '#'+plugin.img_id+'-img-preview',
					minContainerWidth: plugin.settings.mincontainerwidth,
					minContainerHeight: plugin.settings.mincontainerheight,
					ready: function (e) {
						plugin.setMinMaxCrop()
						
					},
					cropstart: function (e) {
						var $cropper = $(e.target);
						plugin.setMinMaxCrop()
					},
					cropmove: function (e) {
						var $cropper = $(e.target);
						// Call getData() or getImageData() or getCanvasData() or
						// whatever fits your needs
						var data = plugin.cropper.getCropBoxData()
						mincrop = plugin.setMinMaxCrop()
						if (mincrop ==1){
							return false;
						}
						// Continue resize
						return true;
					},
					cropend: function (e) {
						Coordinates = plugin.GetCoordinates();
						plugin.SetCoordinates(Coordinates)
						$("#" + plugin.img_id + "_cropped").val(plugin.getCanvas())     
						$(plugin.delete_image_id+"_delete").attr('checked','checked')
						},
						crop: function (e) {
						var data = e.detail;
						},
					zoom: function (e) {
						setTimeout(function () {
								Coordinates = plugin.GetCoordinates();
								plugin.setMinMaxCrop()
								plugin.SetCoordinates(Coordinates)
								$("#" + plugin.img_id + "_cropped").val(plugin.getCanvas())
							$(plugin.delete_image_id+"_delete").attr('checked','checked')
						}, 500);
					},
						
				};
				if(plugin.initiator.full_img_val){
					plugin.initiator.image.src = plugin.initiator.full_img_val
					plugin.showHideConainer(plugin.container,plugin.img_id)
				} else {
					plugin.initiator.image.src =""
					plugin.showHideConainer(plugin.container,plugin.img_id,false)
				}
				//create cropper object
				plugin.cropper = plugin.cropperobj()
				//call cropper init
				plugin.CropperInit()
			},
			plugin.getCanvas= function(settings =plugin.settings , imagetype =plugin.default_ext){
				canvas =''
				if (settings.orginal_extension==true && plugin.uploadedImageType !=plugin.default_ext ){
					canvas = plugin.cropper.getCroppedCanvas().toDataURL()
				} else{
					canvas = plugin.cropper.getCroppedCanvas(plugin.canvas_option(settings)).toDataURL(imagetype)
				}
				return canvas
			}
			plugin.cropperobj = function(){
				plugin.cropper = new plugin.initiator.Cropper(plugin.initiator.image, plugin.crop_options);

				plugin.cropper.destroy();
				plugin.cropper = null;
				$(plugin.container).children(".cropper-container").remove();
				plugin.cropper = new plugin.initiator.Cropper(plugin.initiator.image, plugin.crop_options);
				return  plugin.cropper
			}
			plugin.showHideConainer = function(container,img_id,show = true) {
				if (show) {
					plugin.initiator.container_div.show()
					$(plugin.container).show()
					$('#'+plugin.img_id+'-actions').show()
				} else {
					plugin.initiator.container_div.hide()
					$(plugin.container).hide()
					$('#'+plugin.img_id+'-actions').hide()
				}

			}
			plugin.CropperInit = function() {
				if (!document.createElement('canvas').getContext) {
					$('button[data-method="getCroppedCanvas"]').prop('disabled', true);
				}
			
				if (typeof document.createElement('cropper').style.transition === 'undefined') {
					$('button[data-method="rotate"]').prop('disabled', true);
					$('button[data-method="scale"]').prop('disabled', true);
				}
				// Methods
				plugin.initiator.actions.querySelector('.action-buttons').onclick = function (event) {
					
					var e = event || window.event;
					var target = e.target || e.srcElement;
					var cropped;
					var result;
					var input;
					var data;
				
					if (!plugin.cropper) {
					return;
					}
					while (target !== this) {
					if (target.getAttribute('data-method')) {
						break;
					}
					target = target.parentNode;
					}
					if (target === this || target.disabled || target.className.indexOf('disabled') > -1) {
					return;
					}
					data = {
						method: target.getAttribute('data-method'),
						target: target.getAttribute('data-target'),
						option: target.getAttribute('data-option') || undefined,
						secondOption: target.getAttribute('data-second-option') || undefined
					};
					cropped = plugin.cropper.cropped;
				
					if (data.method) {
					
					if (typeof data.target !== 'undefined') {
						input = document.querySelector(data.target);
						if (!target.hasAttribute('data-option') && data.target && input) {
						try {
							data.option = JSON.parse(input.value);
						} catch (e) {
							console.log(e.message);
						}
						}
					}
					switch (data.method) {
						case 'rotate':
						if (cropped && plugin.crop_options.viewMode > 0) {
							plugin.cropper.clear();
						}
						break;
						case 'delete':
						alert('ghghghhg')
						if (cropped && plugin.crop_options.viewMode > 0) {
							plugin.cropper.clear();
						}
						break;
						case 'getCroppedCanvas':
						try {
							data.option = JSON.parse(data.option);
						} catch (e) {
							console.log(e.message);
						}
						if (plugin.uploadedImageType === 'image/jpeg') {
							if (!data.option) {
							data.option = {};
							}
							data.option.fillColor = '#FFFFFF';
						}
						break;
					}
					
					result = plugin.cropper[data.method](data.option, data.secondOption);     
					switch (data.method) {        
						case 'rotate':
							Coordinates = plugin.GetCoordinates();
							plugin.SetCoordinates(Coordinates)
							setTimeout(function () {
								$("#" + plugin.img_id + "_cropped").val(plugin.getCanvas())
								$(plugin.delete_image_id+"_delete").attr('checked','checked')
							}, 400);
							if (cropped && plugin.crop_options.viewMode > 0) {
								plugin.cropper.crop();
							}
							break;
						case 'move':
							Coordinates = plugin.GetCoordinates();		
							plugin.SetCoordinates(Coordinates)
							$("#" + plugin.img_id + "_cropped").val(plugin.getCanvas())
							$(plugin.delete_image_id+"_delete").attr('checked','checked')
							break;
						case 'reset':
							Coordinates = plugin.GetCoordinates();		
							plugin.SetCoordinates(Coordinates)
							$("#" + plugin.img_id + "_cropped").val(plugin.getCanvas())
							$(plugin.delete_image_id+"_delete").attr('checked','checked')
							mincrop = plugin.setMinMaxCrop()
							break;
						case 'disable':
							plugin.deleteImage()
							break;  
						case 'scaleX':
						case 'scaleY':
							target.setAttribute('data-option', -data.option);
							break;        
						case 'destroy':
							alert('fggfgf')
							plugin.cropper = null;
							if (plugin.uploadedImageURL) {
								URL.revokeObjectURL(plugin.uploadedImageURL);
								plugin.uploadedImageURL = '';
								plugin.initiator.image.src = originalImageURL;
							}
							break;
					}
				
					if (typeof result === 'object' && result !== plugin.cropper && input) {
						try {
						input.value = JSON.stringify(result);
						} catch (e) {
						console.log(e.message);
						}
					}
					}
				};
	
				document.body.onkeydown = function (event) {
					var e = event || window.event;
				
					if (e.target !== this || !plugin.cropper || this.scrollTop > 300) {
					  return;
					}
					switch (e.keyCode) {
					  case 37:
						e.preventDefault();
						plugin.cropper.move(-1, 0);
						break;
				
					  case 38:
						e.preventDefault();
						plugin.cropper.move(0, -1);
						break;
				
					  case 39:
						e.preventDefault();
						plugin.cropper.move(1, 0);
						break;
				
					  case 40:
						e.preventDefault();
						plugin.cropper.move(0, 1);
						break;
					}
				};
				if (URL) {
					
					$(plugin).change(function(){
					//   console.time('Upload #2');
					  var files = this.files;
					  var file;
					  if (plugin.cropper && files && files.length) {
						  file = files[0];
						  imagevalidate = plugin.imageValidations(file)
						  if (imagevalidate['status'] == 'success'){
							if (file && /^image\/\w+/.test(file.type) ) {
								try {
									plugin.uploadedImageType = file.type;
									uploadedImageName = file.name;
									if (imagevalidate['action'] == 'compress'){
										plugin.compressImage(file, plugin)
									} else {
									plugin.ordinaryImage(file)
									}
									//inputImage.value = null;
									// console.timeEnd('Upload #2');
								} catch(err) {
									
									plugin.throwImgException(err)
								}
							} else {
							plugin.throwImgException('Please choose an image file.')
							}
						  } else {
							  
							plugin.throwImgException( imagevalidate['message'])	
						  }
						  
					  }
					  
					});

				} else {
				inputImage.disabled = true;
				inputImage.parentNode.className += ' disabled';
				}
			}
			plugin.GetCoordinates =  function() {
				var cordiantes = {}
				value = plugin.cropper.getData();
				cordiantes['x'] = value.x.toFixed(2);
				cordiantes['y'] = value.y.toFixed(2);
				cordiantes['w'] = value.width.toFixed(2);
				cordiantes['h'] = value.height.toFixed(2);
				cordiantes['r'] = value.rotate.toFixed(2);
				return cordiantes;
			}
			plugin.SetCoordinates =  function(Coordinates) {
				$.each(plugin.coords, function( key, coord ) {
					$("#" + plugin.img_id +'_' +coord).val(Coordinates[coord])
				});
			} 
			plugin.checkFileSize = function(file){
				return filesize =(file.size / 1024/1024).toFixed(2); 
			}
			plugin.ordinaryImage = function (file){
		
				
				if (plugin.uploadedImageURL) {
					URL.revokeObjectURL(plugin.uploadedImageURL);
				}
				let _URL = window.URL || window.webkitURL;
				
				let imageProcess = function(file, callback) {
					let img = new Image();
					img.onload = function(){        
					  if(callback) callback(img);    
					}   
					img.src = _URL.createObjectURL(file); 
				}
				
				imageProcess(file,function(new_image){
					try {
						plugin.setDisplay()
						if (new_image.width < parseFloat(plugin.settings.mincropwidth) || new_image.height < parseFloat(plugin.settings.mincropheight)){
							throw "Please upload image minimum width "+plugin.settings.mincropwidth +'px' + ' and minimum height'+plugin.settings.mincropheight +'px'
								
						}
						plugin.initiator.image.src =new_image.src
					
						plugin.cropper.destroy();
						plugin.cropper = new plugin.initiator.Cropper(plugin.initiator.image, plugin.crop_options);
						setTimeout(function () {
							Coordinates = plugin.GetCoordinates();
							plugin.SetCoordinates(Coordinates)
							full_image = plugin.convertImage(new_image)
							// var FR= new FileReader();
							// FR.addEventListener("load", function(e) {
							// 	$("#" + plugin.img_id + "_full").val(e.target.result)
							// }); 
							// FR.readAsDataURL( file );
							$("#" + plugin.img_id + "_full").val(full_image)
							
							$("#" + plugin.img_id+ "_cropped").val(plugin.getCanvas())
							
						}, 400);
					}catch(err) {
						plugin.throwImgException(err)	
					}
				})
			}
			plugin.throwImgException =function (err){
				var $el = $("#" + plugin.img_id);
				$el.wrap('<form>').closest('form').get(0).reset();
				$el.unwrap();
				window.alert(err);
				// Swal.fire(
				// 	err
				// 	)
			}
			plugin.setDisplay =function(){
				//$("#img-ctr-div").removeAttr('style');
				plugin.showHideConainer(plugin.container, plugin.img_id,true)
				$(plugin.delete_image_id+"_delete").attr('checked','checked')
				$(plugin.delete_image_id).removeAttr('checked')
				$(plugin.delete_image_id + "_deleteonly").removeAttr('checked')
			}
			plugin.convertImage =function(image,type="compress",settings = plugin.settings,ext = plugin.default_ext){
				var canvas=document.createElement("canvas");
				var context=canvas.getContext("2d");
				comps_ratio =1
				if(type =="compress" && image.width >= parseFloat(settings.maxmainimagewidth)){
					comps_ratio = image.width/parseFloat(settings.maxmainimagewidth)
				}
				canvas.width=image.width/comps_ratio;
				canvas.height=image.height/comps_ratio;
				context.drawImage(image,
					0,
					0,
					image.width,
					image.height,
					0,
					0,
					canvas.width,
					canvas.height
				);
				if (settings.orginal_extension==true){
					ext = plugin.uploadedImageType
				}
				if (type=="compress"){
					compres = canvas.toDataURL(ext,settings.fileresolution);
				} else {
					compres = canvas.toDataURL(ext);
				}
				
				return compres
			}
			plugin.compressImage = function (file){
			
				//https://embed.plnkr.co/plunk/oyaVFn
				var FR= new FileReader();
				FR.readAsDataURL( file );
				FR.addEventListener("load", function(e) {
					
					var image2 = new Image();
					image2.onload=function(){
						plugin.setDisplay()
						compres = plugin.convertImage(image2,type="compress")
						plugin.initiator.image.src = plugin.uploadedImageURL = compres
						
						plugin.cropper.destroy();
						plugin.cropper = new plugin.initiator.Cropper(plugin.initiator.image, plugin.crop_options);
						setTimeout(function () {
							
							Coordinates = plugin.GetCoordinates();
							plugin.SetCoordinates(Coordinates)
							$("#" + plugin.img_id + "_full").val(plugin.initiator.image.src)
							$("#" + plugin.img_id + "_cropped").val(plugin.getCanvas())
							
						}, 400);
						
					}
					image2.src=e.target.result;
					
				}); 
			}
			plugin.imageValidations = function(file){
				let return_data={
					'status':'success',
					'action':null,
					'message':'success'
				}
				try {
					size = plugin.checkFileSize(file)
					if (size > parseFloat(plugin.settings.filesize) && plugin.settings.compress ==true){
						//throw "Max file upload size "+plugin.settings.filesize +' MB'
						return_data ={
							'status':'success',
							'action':'compress',
							'message':'success',
						}
					} else if (size > parseFloat(plugin.settings.filesize) && plugin.settings.compress !=true ){
						throw "Max file upload size "+plugin.settings.filesize +' MB'
						
					}
				}
				catch(err) {
					return_data ={
						'status':'failed',
						'action':null,
						'message':err
					}
				}
				return return_data
			}
			plugin.setMinMaxCrop = function (){
				var data = plugin.cropper.getCropBoxData()
				var ImageData = plugin.cropper.getImageData()
				var CanvasData = plugin.cropper.getCanvasData()
				canvas_width = ImageData.naturalWidth/CanvasData.width
				canvas_height = ImageData.naturalHeight/CanvasData.height
				cropped_width = data.width*canvas_width
				cropped_height = data.height*canvas_height
				// var canvasdata = plugin.cropper.getCanvasData();
				flag = 0
				if (plugin.settings.croprestrict ==true){
					if(parseInt(plugin.settings.aspectratio_w) > parseInt(plugin.settings.aspectratio_h)){
						if (parseFloat(cropped_width) <= parseFloat(plugin.settings.mincropwidth)) {
							data.width = parseFloat(plugin.settings.mincropwidth)/canvas_width
							flag =1
						}
						if (parseFloat(cropped_width) > parseFloat(plugin.settings.maxcropwidth)) {
							data.width = parseFloat(plugin.settings.maxcropwidth)/canvas_width
							flag =1
						}
						
						
					} else if(plugin.settings.aspectratio_w < plugin.settings.aspectratio_h) {
						
						if (parseFloat(cropped_height) <= parseFloat(plugin.settings.mincropheight)) {
							
							data.height = parseFloat(plugin.settings.mincropheight)/canvas_height
							flag =1
						}
						if (parseFloat(cropped_height) >= parseFloat(plugin.settings.maxcropheight)) {
							
							data.height = parseFloat(plugin.settings.maxcropheight)/canvas_height
							flag =1
						}
					} else {
						if (parseFloat(cropped_height) <= parseFloat(plugin.settings.mincropheight)) {
							data.height = parseFloat(plugin.settings.mincropheight)/canvas_height
							flag =1
						}
						if (parseFloat(cropped_height) > parseFloat(plugin.settings.maxcropheight)) {
							data.height = parseFloat(plugin.settings.maxcropheight)/canvas_height
							flag =1
						}
						
					}
					if(flag==1){
						plugin.cropper.setCropBoxData(data)
					}
				}
				return flag
			}
			plugin.deleteImage = function (){
				var img_id_split = plugin.img_id.split(/_(.+)/)[1]
				var delete_image_id = "#"+img_id_split+"-clear_id"
				$(delete_image_id+"_delete").attr('checked','checked')
				$(delete_image_id).attr('checked','checked')
				$(delete_image_id+"_deleteonly").attr('checked','checked')
				plugin.showHideConainer(plugin.container,plugin.img_id,false)
				$("#" + plugin.img_id + "_full").val('')
				$("#" + plugin.img_id + "_cropped").val('')
				plugin.cropper.destroy();
				var $el = $("#" + plugin.img_id);
				$el.wrap('<form>').closest('form').get(0).reset();
				$el.unwrap();
			}
			plugin.canvas_option =  function (setConfig){
		
				canvas_data = {
					fillColor: setConfig.fillcolor,
				  }		
				return canvas_data
			}
		
			plugin.init();


	};

}( jQuery ));
$(document).find("[cropper-image]").each(function () {
		
	// CropperCropImage(this);
	// console.time('Function #2');
	$(this).CropperImage()
	// console.timeEnd('Function #2')
});

