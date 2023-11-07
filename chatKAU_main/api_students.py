from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from .serializers import StudentInfoRequestSerializer, StudentSerializer
import requests

class StudentLogin(APIView):
    def post(self, request):
        
        serializer = StudentInfoRequestSerializer(data=request.data)
        if serializer.is_valid():
            student_number = serializer.validated_data['studentNumber']
            password = serializer.validated_data['password']

            try:
                student = Student.objects.get(studentNumber=student_number)
                
                if student.password == password:
                    student_serializer = StudentSerializer(student)
                    return Response(student_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
            
            except Student.DoesNotExist:
                if crawl_and_register(student_number, password):
                    new_student = Student.objects.create(studentNumber=student_number, password=password,
                                                         name='김동김', major='소프트웨어', majorScore=3, generalScore=3, totalScore=3)
                    new_student_serializer = StudentSerializer(new_student)
                    return Response(new_student_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def crawl_and_register(student_number, password):
    if student_number == "1":
        return True
    
    return False