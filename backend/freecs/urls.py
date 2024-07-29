from django.urls import path
from .views import CategoryCreateView, CategoryView, CourseCreateView, CourseView, EnrollmentCreateView, EnrollmentListView, InstructorListView, InstructorUpdateView, LoginView, PreferredCoursesView, PreferenceCreateView, SignUpView, UserProfileView,UserChangePasswordView,SendPasswordRestEmailView,UserRestPasswordEmailView,SearchView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/',UserProfileView.as_view(),name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(),name='changepassword'),
    path('send-reset/',SendPasswordRestEmailView.as_view(),name='sendpassword'),
    path('send-reset/<uid>/<token>/',UserRestPasswordEmailView.as_view(),name='sendpassword'),
    path('instructors/', InstructorListView.as_view(), name='instructor-list'),
    path('instructors/<int:instructor_id>/update/', InstructorUpdateView.as_view(), name='instructor-update'),
    path('category/',CategoryView.as_view(),name='category'),
    path('category/add',CategoryCreateView.as_view(),name='category-add'),
    path('courses/',CourseView.as_view(),name='courses'),
    path('courses/add',CourseCreateView.as_view(),name='courses-create'),
    path('enrollment/',EnrollmentListView.as_view(),name='enrollment'),
    path('enrollment/add',EnrollmentCreateView.as_view(),name='enrollment-create'),
    path('preferences/add',PreferenceCreateView.as_view(),name='preferences-create'),
    path('preferred-courses/<int:member_id>/', PreferredCoursesView.as_view(), name='preferred_courses'),
    path('search/',SearchView.as_view(),name='search'),
    
]
