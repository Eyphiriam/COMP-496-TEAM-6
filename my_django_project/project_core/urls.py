from django.urls import path
from . import views  
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface
    path('', views.index, name='index'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('view_history/', views.view_history, name='view_history'),
    path('resubmit/<int:image_id>/', views.resubmit, name='resubmit'),
    path('results/<int:image_id>/', views.show_result, name='show_result'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
