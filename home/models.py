from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('Viewer', 'Viewer'),
        ('Analyst', 'Analyst'),
        ('Admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='Viewer')

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.user_type = 'Admin'
        super().save(*args, **kwargs)


class Record(models.Model):
    amount = models.PositiveIntegerField()
    type = models.CharField(choices=[('Income', 'Income'), ('Expense', 'Expense')])
    category = models.CharField(max_length=100, choices=[('Salary', 'Salary'), ('Friend', 'Friend'), ('Business', 'Business'), ('Food', 'Food'), ('Transportation', 'Transportation'), ('Entertainment', 'Entertainment'), ('Groceries', 'Groceries'), ('Healthcare', 'Healthcare'), ('Other', 'Other')])
    time = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
