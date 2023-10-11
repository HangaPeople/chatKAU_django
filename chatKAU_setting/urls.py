from django.contrib import admin
from django.urls import path
import chatKAU_main.views as views
import chatKAU_main.shortcutMenu as shortcut

urlpatterns = [
    path("admin/", admin.site.urls),
    path('langchain', views.langchain, name='langchain'),
    path('', views.index, name='index'),
    
]
