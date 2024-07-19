from django.db import models
from django.contrib.auth import get_user_model
User=get_user_model()
# Create your models here.
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
