from django.db import models
from django.contrib.auth.models import User

# Member table with default user
class Member(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_instructor = models.BooleanField()

    def __str__(self):
        return self.user.username


# Instructor table with default member
class Instructor(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    skills = models.JSONField(default=dict)  # Use a callable default
    bio = models.TextField(null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    rate_per_hour = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.member.user.username} - {self.skills or 'No skills'}"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Categories"


# Course Model
class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ManyToManyField(Category)
    instructors = models.ManyToManyField(Instructor)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class Enrollment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    course = models.OneToOneField(Course, on_delete=models.CASCADE, default=None)
    enrollment_date = models.DateTimeField(auto_now_add=True)
class Preference(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)
    

    def __str__(self) -> str:
        return self.member.user.username
