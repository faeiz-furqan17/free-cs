
from django.contrib import admin
from django.contrib.auth.models import User

from .models import Member,Instructor,Category,Course,Enrollment,Preference


class MemberInline(admin.StackedInline):
    model = Member
    fields=['is_instructor']
    extra = 0


class UserAdmin(admin.ModelAdmin):
    inlines = [MemberInline]
    list_display=['first_name', 'last_name','email']


class MemberAdmin(admin.ModelAdmin):
    list_display = ["get_username", "get_email"]
    def get_username(self, obj):
        return obj.user.username
    def get_email(self,obj):
        return obj.user.email
    get_email.short_description = "Email"
    
class InstructorAdmin(admin.ModelAdmin):
    list_display=["get_teacher_name","rate_per_hour"]
    fieldsets=[
        ("Instructor Details", {"fields": ["member", "bio", "experience", "rate_per_hour"]}),
        ("Instructor Skills", {"classes":["collapse"], "fields": ["skills"]})
    ]
    def get_teacher_name(self,obj):
        return obj.member.user.first_name + " " + obj.member.user.last_name
    def get_skills(self, obj):
        return list(obj.skills.values())
    
    get_teacher_name.short_description = "Teacher Name"
    get_skills.short_description = "Skills"
    
class PreferenceAdmin(admin.ModelAdmin):
    list_filter = ["category"]   

admin.site.register(Member,MemberAdmin)
admin.site.register(Instructor,InstructorAdmin)
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Preference, PreferenceAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)