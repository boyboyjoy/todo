from django.contrib.auth.models import User
from django.db import models

from TODO import settings


class Task(models.Model):
    description = models.TextField(max_length=200, blank=False)
    scheduled_deadline = models.DateField(auto_now_add=False)
    real_deadline = models.DateField(auto_now_add=True)
    status = [('TODO', 'TODO'),  ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('CANCELED', 'CANCELED')]
    task_status = models.CharField(max_length=11, choices=status, default='TODO')
    file = models.FileField(default=None, blank=True)
    parent_board = models.ForeignKey('Board', on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.description


class Board(models.Model):
    title = models.CharField(max_length=30, blank=False)
    user_creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, blank=False, default='#AAAAAA')

    def __str__(self):
        return self.title


class Tag(models.Model):
    text = models.CharField(max_length=15, blank=False, default=None)
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.text

