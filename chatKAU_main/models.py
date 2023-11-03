from django.db import models

class SchoolInfo(models.Model):
    keyword = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    origin = models.CharField(max_length=100, default='user')

    def __str__(self):
        return self.keyword
