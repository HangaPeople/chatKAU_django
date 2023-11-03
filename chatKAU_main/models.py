from django.db import models

class SchoolInfo(models.Model):
    keyword = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    origin = models.CharField(max_length=100, default='user')

    def __str__(self):
        return self.keyword

class Student(models.Model):
    year = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    majorScore = models.DecimalField(max_digits=5, decimal_places=2)
    generalScore = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class StudentInfoRequest:
    studentNumber = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=100)