from urllib.request import BaseHandler
from django import forms
from django.shortcuts import redirect
from rest_framework import status,generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import stripe
from .models import Course, Enrollment, Instructor,Category, Member,Preference
from .serializers import CategorySerializer, CourseCreateUpdateSerializer, CourseSerializer, EnrollmentCreateSerializer, EnrollmentSerializer, InstructorSerializer, InstructorUpdateSerializer, MemberSerializer, PreferenceCreateSerializer, ResetPasswordSerializer, SendPasswordResetEmailSerialize,  UserLoginSerializer, UserProfileSerializer,UserChangePasswordSerializer, UserSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from django.core.mail import send_mail
from django.conf import settings


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SignUpView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        try:
            user_serializer = UserSerializer(data=request.data)
            if user_serializer.is_valid(raise_exception=True):
                try:
                    user = user_serializer.save()
                except IntegrityError as e:
                    if 'unique constraint' in str(e).lower():
                        return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
                    raise e
                

                dataDic={
                    'user':user.id ,
                    'is_instructor':request.data.get('is_instructor')
                    
                    
                    
                }
                print(dataDic)
                member_serializer = MemberSerializer(data=dataDic)
                if member_serializer.is_valid():
                    member_serializer.save(user=user)
                    token = get_tokens_for_user(user)
                    print(member_serializer.data)
                    return Response({"token": token, "data": member_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    print(member_serializer.errors)
                    return Response(member_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as e:
            return Response({"error": "Validation Error", "details": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"error": "Integrity Error", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            return Response({"error": "Database Error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ObjectDoesNotExist as e:
            return Response({"error": "Object Not Found", "details": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#instructor list view 
class InstructorListView(APIView):
    def get(self ,request):
        instructors = Instructor.objects.all()
        serializer = InstructorSerializer(instructors, many=True)
     
        return Response({"data":serializer.data}, status=status.HTTP_200_OK)
    
    
#updating Instructor view
class InstructorUpdateView(APIView):
    

    
    def put(self, request, instructor_id):
        instructor = Instructor.objects.get(id=instructor_id)
        serializer = InstructorUpdateSerializer(instructor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

#show categories
class CategoryView(APIView):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
#create category view
class CategoryCreateView(generics.CreateAPIView):
    
    serializer_class = CategorySerializer
    
class PreferenceCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user

        # Validate that the user is a member
        try:
            member = Member.objects.get(user=user)
        except Member.DoesNotExist:
            return Response({"error": "User must be a member to create preferences."}, status=status.HTTP_400_BAD_REQUEST)

        # Include member in the request data
        dataDict={
            'member':{},
            'category':request.data.copy()
            
        }
        data = dataDict.copy()  
        print(member.id)
        print(data)
        print(data['member'])
        data['member'] = member.id  # Ensure the member ID is included in the data

        serializer = PreferenceCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PreferredCoursesView(APIView):
    def get(self, request, member_id, format=None):

        preferences_categories = Preference.objects.filter(member__id=member_id).values('category')
        courses=Course.objects.filter(category__in = preferences_categories).distinct()

        serializer= CourseSerializer(courses, many=True)
        return Response(serializer.data, 200)

class SearchView(APIView):
    def post(self, request, format=None):
        search_text = request.data.get('search_text', None)
        
        if not search_text:
            return Response({"detail": "No search text provided"}, status=status.HTTP_400_BAD_REQUEST)

        else:
             courses = Course.objects.filter(Q(name__istartswith=request.data.get('search_text'))| Q(category__name__iregex=request.data.get('search_text')))
             
             course_serializer = CourseSerializer(courses, many=True)
          
             return Response({"Courses":course_serializer.data,}, 200)
    

#course create         

class CourseCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user = request.user
        
        try:
            member = Member.objects.get(user=user)
            instructor = Instructor.objects.get(member=member)
            if not member.is_instructor:
                return ValidationError("Only instructors can create courses.")
        except Member.DoesNotExist:
            return ValidationError("User must be a member to create courses.")
        data = request.data.copy()

        data['instructors'] = [instructor.id]
        print(data)
        serializer = CourseCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CourseView(APIView):
    def get(self, request, *args, **kwargs):
        courses = Course.objects.all()
        paginator = LimitOffsetPagination()
        result_page = paginator.paginate_queryset(courses, request)
        serializer = CourseSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



class EnrollmentListView(APIView):
    def get(self, request, *args, **kwargs):
        enrollments = Enrollment.objects.all()
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
#enrollment create 


class EnrollmentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        print(request.user.username)

        # Validate that the user is a member
        try:
            member = Member.objects.get(user=user)
        except Member.DoesNotExist:
            return Response({"error": "User must be a member to create preferences."}, status=status.HTTP_400_BAD_REQUEST)

        print(request.data)
        print("*********************************")

        dataDict = {
            'member': {},
            'course': request.data.get('course'),
        }
        data = dataDict.copy()
        data['member'] = member.id
        print(data)
        print("data to go here")

        serializer = EnrollmentCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            # Send an email to the user after successful enrollment
            subject = 'Enrollment Confirmation'
            message = f'Dear {user.username},\n\nYou have successfully enrolled in the course with ID {data["course"]}.'
            recipient_list = [user.email]

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request, format=None):
        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                username = serializer.validated_data.get('username')
                password = serializer.validated_data.get('password')
                print(f"Attempting to authenticate user: {username}")  # Debug print
                
                user = authenticate(username=username, password=password)
                
                if user is not None:
                    token = get_tokens_for_user(user)
                    print("Authentication successful")  # Debug print
                    return Response({'msg': 'Login successful', "token": token, "id": user.id}, status=status.HTTP_200_OK)
                else:
                    print("Authentication failed")  # Debug print
                    return Response({'errors': {'non_field_errors': ['Username or password not valid']}}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"An error occurred: {str(e)}")  # Debug print
            return Response({'errors': {'non_field_errors': ['An unexpected error occurred']}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UserProfileView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, format=None):
      
        print(request.user)

        serializer = UserProfileSerializer(request.user)
        print(serializer.data)
    
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Password changed successfully', "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class SendPasswordRestEmailView(APIView):
    def post(self,request,format = None):
        serializer = SendPasswordResetEmailSerialize(data=request.data)
        if serializer.is_valid(raise_exception=True):
        
            return Response({'msg': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)
        
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    


class UserRestPasswordEmailView(APIView):
        def post(self,request,uid,token,format = None):
            serializers = ResetPasswordSerializer(data=request.data,context={'token':token,'uid':uid})
            if serializers.is_valid(raise_exception=True):
                return Response({'msg': 'Password reset successful'}, status=status.HTTP_200_OK)
            
            return Response({'errors': serializers.errors}, status=status.HTTP_400_BAD_REQUEST) 

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            

            return Response({"msg": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)   

from django.http import HttpResponseRedirect
       
stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateStripeCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            course = Course.objects.get(id=request.data.get('courseID'))
            total_price = course.price

            # Create a Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': course.name,
                                'description': course.description,
                            },
                            'unit_amount': int(total_price * 100),
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f'http://localhost:3000/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url='http://localhost:3000/cancel',
                metadata={
                    'user_id': user.id,
                    'course_id': course.id,
                },
            )

            print({
                'total_price': total_price,
                'checkout_session_id': checkout_session.id,
                'course_name': course.name,
                'course_description': course.description,
                'user_email': user.email,
                'user_id': user.id,
                'course_id': course.id,
                'checkou_session_url': checkout_session.url
            })

            return HttpResponseRedirect(checkout_session.url)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)





