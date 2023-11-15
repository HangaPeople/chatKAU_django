from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import chatKAU_main.views as views
from chatKAU_main.shortcutMenu import SchoolInfoByKeyword
from chatKAU_main.api_students import StudentLogin
from chatKAU_main.crawling import crawling_menu

urlpatterns = [
    path("admin/", admin.site.urls),
    path('langchain', views.langchain, name='langchain'),
    path('', views.index, name='index'),
    
    path('api/shortcut/<str:keyword>', SchoolInfoByKeyword.as_view(), name='SchoolInfoByKeyword'),
    path('response/isGood', views.saveChatHistory, name='saveChatHistory'),
    path('user/login', StudentLogin.as_view(), name='student-login'),
    path('crawling/menu', crawling_menu, name='crawlingMenu'),
    path('saved', views.responseSavedChat, name='saved'),
]

router = routers.DefaultRouter()

schema_view = get_schema_view(
    openapi.Info(
        title = "chatKAU API 문서",
        default_version = 'v1',
        description = "항공대학교 챗봇입니다.",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]