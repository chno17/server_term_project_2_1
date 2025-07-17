from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200, default='CalenderEvent')
    keyword = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
class Account(models.Model):
    title = models.CharField(max_length=100)
    amount = models.IntegerField()
    date = models.DateField()