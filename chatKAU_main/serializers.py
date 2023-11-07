from rest_framework import serializers
from .models import SchoolInfo
from .models import Student

class SchoolInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolInfo
        fields = ['keyword', 'content', 'origin']
        
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['studentNumber', 'password', 'name', 'major', 'majorScore', 'generalScore', 'totalScore']

class StudentInfoRequestSerializer(serializers.Serializer):
    studentNumber = serializers.CharField(max_length=10)
    password = serializers.CharField(max_length=100)
