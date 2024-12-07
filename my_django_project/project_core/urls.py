from django.urls import path
from . import views  
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),  # The home page that renders the index.html
    path('upload/', views.upload_image, name='upload_image'),
    path('history/', views.view_history, name='view_history'),
    path('show_result/<int:image_id>/', views.show_result, name='show_result'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
