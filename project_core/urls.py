from django.urls import path
from . import views  
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Image upload API
    path('upload/', views.upload_image, name='upload_image'),
    path('process_image/', views.process_image, name='process_image'),  
]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
