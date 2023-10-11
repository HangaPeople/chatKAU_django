from django.contrib import admin
from django.urls import path
import chatKAU_main.views as views
from chatKAU_main.shortcutMenu import SchoolInfoByKeyword

urlpatterns = [
    path("admin/", admin.site.urls),
    path('langchain', views.langchain, name='langchain'),
    path('', views.index, name='index'),
    
    path('api/shortcut/<str:keyword>', SchoolInfoByKeyword.as_view(), name='SchoolInfoByKeyword')
]
