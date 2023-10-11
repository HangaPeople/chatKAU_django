from django.contrib import admin
from django.urls import path
import chatKAU_main.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('langchain', chatKAU_main.views.langchain, name='langchain'),
    
    path('', chatKAU_main.views.index, name='index'),
]
