# project_core/views.py
from django.shortcuts import render
from django.http import JsonResponse
from .forms import ImageUploadForm  # You'll need to create this form
from .models import UploadedImage  # You need a model to save the uploaded images
from .utils import process_image_and_predict  # The function to process and predict using the model
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view

def index(request):
    return render(request, 'core/index.html')

def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        uploaded_image = UploadedImage.objects.create(image=image)
        result = process_image_and_predict(uploaded_image.image.path)  # Assuming a function to handle the model prediction
        uploaded_image.result = result
        uploaded_image.save()
        return JsonResponse({
            'message': 'File uploaded successfully!',
            'image_url': uploaded_image.image.url,
            'result': result
        })
    return JsonResponse({'error': 'No file uploaded'}, status=400)

def view_history(request):
    images = UploadedImage.objects.all().order_by('-timestamp')
    return render(request, 'core/view_history.html', {'images': images})

def show_result(request, image_id):
    uploaded_image = get_object_or_404(UploadedImage, id=image_id)
    
    # Return a JSON response with the result
    return JsonResponse({
        'message': 'Prediction result',
        'image_url': uploaded_image.image.url,
        'result': uploaded_image.result,
    })

def resubmit_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        uploaded_image = UploadedImage.objects.create(image=image, result="Resubmitted Result")
        return JsonResponse({'success': True, 'image_url': uploaded_image.image.url})
    return JsonResponse({'success': False}, status=400)

@api_view(['POST'])
def process_image(request):
    # Check if the request contains an image
    if 'image' not in request.FILES:
        return Response({"error": "No image provided"}, status=400)

    # Pass the uploaded image to the utility function
    result = process_image_and_predict(request.FILES['image'])

    if "error" in result:
        return Response(result, status=500)

    return Response(result, status=200)