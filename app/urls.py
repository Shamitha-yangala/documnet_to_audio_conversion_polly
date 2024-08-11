from django.urls import path
from . import views

urlpatterns = [
   
    path('', views.doc_file_upload, name='doc_file_upload'),
    path('get_genders/', views.get_genders, name='get_genders'),
    path('get_voices/',views. get_voices, name='get_voices')
   
]
