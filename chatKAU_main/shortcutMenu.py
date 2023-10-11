from rest_framework import generics
from .models import SchoolInfo
from .serializers import SchoolInfoSerializer

class SchoolInfoByKeyword(generics.ListAPIView):
    serializer_class = SchoolInfoSerializer

    def get_queryset(self):
        keyword = self.kwargs['keyword']
        return SchoolInfo.objects.filter(keyword=keyword)