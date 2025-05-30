from django.contrib.auth.models import Permission,Group
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..serializers import UserSerializer
from vpms.api.custom_pagination import CustomPagination
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import F, Value
from django.db.models.functions import Concat
import json
from django.conf import settings
from ..models import Staff,EmailResetCode

from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.sites.models import Site
from ..models import EmailVerification
import os
from dotenv import load_dotenv
import random
from rest_framework.views import APIView

load_dotenv()

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
SITE_URL = settings.SITE_URL

User = get_user_model()

# an API for getting the list of all users
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,DjangoModelPermissions]
    filter_backends = [OrderingFilter,SearchFilter]
    search_fields = [field.name for field in User._meta.fields]
    ordering_fields = [field.name for field in User._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination


#an API for getting a specific user by ID
class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

#an API for deactivating a user
class UserDestroyView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def handle_exception(self, exc):
        if isinstance(exc,NotFound):
            return Response({"error":"There is no user with the given id!"},status=status.HTTP_400_BAD_REQUEST)

        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        user_to_deactivate = self.get_object()
        if not user_to_deactivate:
            return Response({"error":"There is no user with the given id!"},status=status.HTTP_404_NOT_FOUND)
        user_to_deactivate.is_active = False
        user_to_deactivate.save()
        return Response({"message":"user deactivated successfully"},status=status.HTTP_200_OK)

#an API for creating a user
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]



@api_view(["POST"])
def activate_user(request,id):
    try:
        user = User.objects.get(pk=id)
    except:
        return Response({"error":"there is no user with the given id"},status=status.HTTP_404_NOT_FOUND)
    user.is_active = True
    user.save()
    return Response({"message":"user is activated successfully!"},status=status.HTTP_200_OK)

#-------------------------------------an API for assigning permissions to users, we can either remove or add permissions to users-----------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setUserPermissions(request):
    if not request.user.has_perm('auth.change_user'):
        return Response({"message":"you don't have the permission to set user's permissions"},status=status.HTTP_403_FORBIDDEN)
    user_id = request.data.get("user_id")
    permission_code_names = request.data.get("permissions") 
    if not user_id or not permission_code_names:
        return Response({"message":"please provide user_id and permissions"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"message":"user does not exist"},status=status.HTTP_404_NOT_FOUND)
    permissions = Permission.objects.filter(codename__in=permission_code_names)
    user.user_permissions.clear()
    user.user_permissions.set(permissions)
    return Response({"message":"permissions assigned to user succssfully!"},status=status.HTTP_200_OK)


#-------------------------------------an API for assigning groups to users, we can either remove or add groups to users-----------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setUserGroups(request):
    if not request.user.has_perm('auth.change_user'):
        return Response({"message":"you don't have the permission to set user's groups"},status=status.HTTP_403_FORBIDDEN)
    user_id = request.data.get("user")
    group_names = request.data.get("groups") 
    if not user_id or not group_names:
        return Response({"message":"please provide user_id and permissions"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=user_id)
    except Group.DoesNotExist:
        return Response({"message":"User does not exist"},status=status.HTTP_404_NOT_FOUND)
    groups = Group.objects.filter(name__in=group_names)
    if not groups:
        return Response({"message":"group not found!"},status=status.HTTP_404_NOT_FOUND)
    user.groups.clear()
    user.groups.set(groups)
    return Response({"message":"groups assigned to user succssfully!"},status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([])
def send_password_reset_email(request):
    email = request.data.get("email")
    if not email:
        return Response({"error":"please provide email!"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error":"there is no user with the provided email"},status=status.HTTP_404_NOT_FOUND)
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    current_site = get_current_site(request)
    dummy_site = "http://localhost:3000/en/reset-password/" + f'{token}'
    reset_link = f"https://{current_site.domain}/reset-password/{token}"
    
    
    
    # Send email with both plain text and HTML content
    send_mail(
        subject="Password reset request",
        message=f"Click the link below to reset your password:\n\n{current_site}",  # Plain text version
        from_email=EMAIL_HOST_USER,
        recipient_list=[email])


    return Response({"message":"password reset email was sent successfully"},status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([])
def reset_password(request,token):
    acces_token = AccessToken(token)
    try:
        user = User.objects.get(id=acces_token["user_id"])
    except User.DoesNotExist:
        return Response({"error":"Invalid or expired token"},status=status.HTTP_400_BAD_REQUEST)
    new_password = request.data.get("password")
    user.set_password(new_password)
    user.save()

    return Response({"message":"password reset successfully!"},status=status.HTTP_200_OK)


# an API for the owner to change his password
@api_view(["POST"])
@permission_classes([])
def change_password(request):
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    user = request.user

    if not user.check_password(old_password):
        return Response({"error":"wrong old password!"},status=status.HTTP_400_BAD_REQUEST)
    user.set_password(new_password)
    user.save()
    return Response({"message":"password changed successfully!"},status=status.HTTP_200_OK)
    



#an API for sending a reset code to the user's email
@api_view(["POST"])
@permission_classes([])
def send_password_reset_email_phone(request):
    email = request.data.get("email")
    if not email:
        return Response({"error":"please provide email!"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error":"there is no user with the provided email"},status=status.HTTP_404_NOT_FOUND)
    code = f"{random.randint(1000, 9999)}"
    EmailResetCode.objects.create(user=user,code=code)

    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    current_site = get_current_site(request)
    dummy_site = "http://localhost:3000/en/reset-password/" + f'{token}'
    reset_link = f"https://{current_site.domain}/reset-password/{token}"
    
    
    
    # Send email with both plain text and HTML content
    send_mail(
        subject="Password reset request",
        message=f"Your verification code is: {code}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email]
    )

    return Response({"message":"password reset code was sent to your email successfully"},status=status.HTTP_200_OK)



class VerifyResetCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        try:
           user = User.objects.get(email=email)
        except User.DoesNotExist:
           return Response({"error":"there is no user with the provided email"},status=status.HTTP_404_NOT_FOUND)
        try:
            record = EmailResetCode.objects.filter(user=user, code=code, is_used=False).latest('created_at')
        except EmailResetCode.DoesNotExist:
            return Response({"error": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

        if record.is_expired():
            return Response({"error": "Code expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark as used and allow password reset to proceed
        record.is_used = True
        record.save()
        return Response({"message": "Code verified successfully."}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([])
def reset_password_phone(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error":"There is no user with the given email"},status=status.HTTP_400_BAD_REQUEST)
    
    try:
            # Ensure a valid, unused, non-expired verification code exists
        verification = EmailVerification.objects.filter(email=email, is_used=True).latest("created_at")
    except EmailVerification.DoesNotExist:
        return Response({"error": "No verified code found for this email."}, status=status.HTTP_400_BAD_REQUEST)

    if verification.is_expired():
        return Response({"error": "Verification expired. Request a new code."}, status=status.HTTP_400_BAD_REQUEST)

    new_password = request.data.get("password")
    user.set_password(new_password)
    user.save()

    return Response({"message":"password reset successfully!"},status=status.HTTP_200_OK)



 

@api_view(["POST"])
@permission_classes([])
def get_user_profile(request):
    access_token = AccessToken((request.data.get("access_token")))
    try:
        user = User.objects.get(id=access_token['user_id'])
        
        if user.profile_picture and hasattr(user.profile_picture, 'url'):
           profile_pic_url = SITE_URL+str(user.profile_picture.url)
        else:
           profile_pic_url = None
    except User.DoesNotExist:
        return Response({"error": "Invalid or expired token"},status=status.HTTP_400_BAD_REQUEST)
    return Response({"user_id":user.pk,"first_name":user.first_name,"middle_name":user.middle_name,
                     "last_name":user.last_name,"email":user.email,"phone_number":user.phone_number,"user_permissions":user.get_all_permissions(),
                     "groups":user.groups.values_list('name',flat=True),"profile_picture":profile_pic_url},status=status.HTTP_200_OK)




@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request,id):
    
    try:
        user = User.objects.get(id=id)
        if not (request.user.id == user.id) and (not request.user.is_superuser):
            return Response({"message":"Unauthorized accesss!"},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({"error":"user with the given id does not exist!"},status=status.HTTP_400_BAD_REQUEST)
    user_permissions = request.data.get("user_permissions",[])
    user_groups = request.data.get("groups",[])
    first_name = request.data.get("first_name")
    middle_name = request.data.get("middle_name")
    last_name = request.data.get("last_name")
    address = request.data.get("address")
    phone_number = request.data.get("phone_number")
    #is_active = request.data.get("is_get")
    is_superuser = request.data.get("is_superuser")
    profile_picture = request.FILES.get("profile_picture")

    if user_permissions:
        permissions = Permission.objects.filter(codename__in=user_permissions)
        user.user_permissions.clear()
        user.user_permissions.set( permissions)
    if user_groups:
        groups = Group.objects.filter(name__in=user_groups)
        user.groups.clear()
        user.groups.set(groups)
    if first_name:
        user.first_name = first_name
    if middle_name:
        user.middle_name = middle_name
    if last_name:
        user.last_name = last_name
    if address:
        user.address = address
    if phone_number:
        user.phone_number = phone_number
    if is_superuser:
        user.is_superuser = is_superuser
    if profile_picture:
        user.profile_picture = profile_picture

    user.save()

    return Response({"message":"successfully updated user!"},status=status.HTTP_200_OK)





class GetOwners(generics.ListAPIView):
    queryset = User.objects.filter(groups__name="owner")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,DjangoModelPermissions]
    filter_backends = [OrderingFilter,SearchFilter]
    search_fields = [field.name for field in User._meta.fields]
    ordering_fields = [field.name for field in User._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def create_staff(request,owner_id,email,first_name,middle_name,last_name,password):
    try:
        owner = User.objects.get(owner_id)
    except:
        return Response({"error":"There is no user with the given owner id"},status=status.HTTP_400_BAD_REQUEST)
    if not owner.groups.filter(name='owner').exists():
        return Response({"error":"There is no owner with the given owner id"},status=status.HTTP_400_BAD_REQUEST)
    
    staff_user = User()
    staff_user.email = email
    staff_user.first_name = first_name
    staff_user.middle_name = middle_name
    staff_user.last_name = last_name
    groups = Group.objects.filter(name='staff')
    staff_user.groups.clear()
    staff_user.groups.set(groups)
    staff_user.set_password(password)
    staff_user.save()

    staff = Staff()
    staff.staff_user = staff_user
    staff.owner = owner
    staff.save()

    

    

    return Response({"message":"successfully created user"},status=status.HTTP_200_OK)






@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up(request):
        if User.objects.filter(email=request.data.get("email")).count()>0:
            return Response({"error":"This email already exists in the system"},status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(data=request.data)
    #if serializer.is_valid():
        #if the user already signed up but didn't verify his account, delete verfication UUID's
        if User.objects.filter(email=request.data.get("email"),is_active=False).count() > 0:
            EmailVerification.objects.filter(user=User.objects.filter(email=request.data.get("email"),is_active=False).first()).delete()
            verification = EmailVerification.objects.create(user=User.objects.filter(email=request.data.get("email"),is_active=False).first())
        
        #if the user hasn't signed up, create him first
        else:
            if User.objects.filter(email=request.data.get("email")).count() > 0:
                return Response({"error":"This email already exists in the system"},status=status.HTTP_403_FORBIDDEN)
            user = User()
            user.email = request.data.get("email")
            user.is_active=False
            user.set_password(request.data.get("password"))
            user.save()
            #if serializer.is_valid():
            #    user = serializer.save(is_active=False)  # Initially set user as inactive
            verification = EmailVerification.objects.create(user=user)
        current_site = request.build_absolute_uri('/')
        mail_subject = 'Verify your email address'
        relative_link = "api/verify-email/"+str(verification.token)#reverse('verify_email', kwargs={'token': str(verification.token)})
        absolute_url = f'http://{current_site}{relative_link}'  # Adjust protocol if needed
        message = f'Hi ,\n\nPlease click on the link below to verify your email address and complete your signup:\n\n{absolute_url}'
        send_mail(mail_subject, message, EMAIL_HOST_USER, [request.data.get("email")])
        return Response({'message': 'Registration successful. Please check your email to verify your account.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    try:
        verification = EmailVerification.objects.get(token=token)
        user = verification.user
        if not user.is_active:
            user.is_active = True
            user.save()
            verification.delete()  # Token can be used only once
            send_mail("verification successful", "Your email has been successfully verified. You can now log in.", EMAIL_HOST_USER, [user.email])
            return Response({'message': 'Your email has been successfully verified. You can now log in.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Your email has already been verified.'}, status=status.HTTP_200_OK)
    except EmailVerification.DoesNotExist:
        return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)
   