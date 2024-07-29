from rest_framework import serializers 

from django.contrib.auth.models import User
from .models import Category, Course, Enrollment, Instructor, Member, Preference
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password','email','first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Member
        fields = ['user', 'is_instructor']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        member, created = Member.objects.update_or_create(user=user, **validated_data)
        if member.is_instructor:
            Instructor.objects.create(member=member)
        return member
    
    #instructor list serializer 
class InstructorSerializer(serializers.ModelSerializer):
    member=MemberSerializer()
    class Meta:
        model = Instructor
        fields = ['member', 'id','skills', 'bio', 'experience', 'rate_per_hour']

#Updating Values for the Instructor
class InstructorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = ['skills', 'bio', 'experience', 'rate_per_hour']
#Preference Create 
class PreferenceCreateSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(),many = True)
    class Meta:
        model = Preference
        fields = ['id','member' ,'category',]

    
        
#Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name','id']
#courses Serializer
class CourseSerializer(serializers.ModelSerializer):
    instructors = InstructorSerializer(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'category', 'instructors', 'price', 'duration']

class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    instructors = serializers.PrimaryKeyRelatedField(queryset=Instructor.objects.all(), many=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'category', 'instructors', 'price', 'duration']


        
        
#Enrollment Serializer

class EnrollmentSerializer(serializers.ModelSerializer):
    member=MemberSerializer()
    course = CourseSerializer(many=True ,read_only=True)
    class Meta:
        model = Enrollment
        fields=['id','course', 'member','enrollment_date']

#Enrollment Create Serializer
    
        
class EnrollmentCreateSerializer(serializers.ModelSerializer):
    member=MemberSerializer()
    course = CourseSerializer(many=True )
    class Meta:
        model = Enrollment
        fields=['id','course', 'member','enrollment_date']
        
        
        
class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)
    class  Meta:
        model=User
        fields=['username', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username', 'email']

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']
        
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        
        if password != password2:
            raise serializers.ValidationError("Passwords must match.")
        
        user.set_password(password)
        user.save()
        
        return attrs
    
class SendPasswordResetEmailSerialize(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = f'http://127.0.0.1:8000/send-reset/{uid}/{token}/'
            
            # Send email
            send_mail(
                'Password Reset Request',
                f'Click the link below to reset your password:\n{link}',
                'from@example.com',  # Replace with your "from" email
                [email],
                fail_silently=False,
            )
            
            return attrs
        else:
            raise serializers.ValidationError("Email does not exist.")

class ResetPasswordSerializer(serializers.Serializer):
     password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
     password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

     class Meta:
        fields = ['password', 'password2']
        
     def validate(self, attrs):
        try:
             password = attrs.get('password')
             password2 = attrs.get('password2')
             uid = self.context.get('uid')
             token = self.context.get('token')
                
             if password != password2:
                raise serializers.ValidationError("Passwords must match.")
             id = urlsafe_base64_decode(uid).decode('utf-8')
             user = User.objects.get(id=id)
            
             if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is invalid.")
             user.set_password(password)
             user.save()
        
             return attrs
        except DjangoUnicodeDecodeError as identifier:
             PasswordResetTokenGenerator().check_token(user, token)
             raise serializers.ValidationError("Token is invalid.")