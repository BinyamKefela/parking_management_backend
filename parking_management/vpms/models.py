from django.db import models
from django.contrib.auth.models import  AbstractUser,AbstractBaseUser,BaseUserManager,PermissionsMixin,Group
from django.conf import settings
from django.contrib.auth import get_user_model
from django.conf import settings
# Create your models here.



from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import os
from django.core.exceptions import ValidationError
from datetime import timedelta

import uuid

SITE_URL = settings.SITE_URL


def validate_uploaded_image_extension(value):
    valid_extensions = ['.png','.jpg','.jpeg','.PNG','.JPG','.JPEG']
    ext = os.path.splitext(value.name)[1]
    if not ext in valid_extensions:
        raise ValidationError('Unsupported filed extension')
        

def get_upload_path(instance,filename):
    ext = filename.split('.')[-1]
    new_file_name = SITE_URL+"/profiles/"+f'{instance.id}.{ext}'
    return new_file_name


# Custom manager for user model
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    


class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30,null=True)
    middle_name = models.CharField(max_length=30,null=True)
    last_name = models.CharField(max_length=30,null=True)
    phone_number = models.CharField(max_length=100,null=True)
    address = models.CharField(max_length=100,null=True)
    profile_picture = models.FileField(upload_to=get_upload_path,validators=[validate_uploaded_image_extension],null=True,blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Make groups and user_permissions optional by adding blank=True and null=True
    groups = models.ManyToManyField(
        'auth.Group', 
        blank=True,
        null=True, 
        related_name='customuser_set', 
        related_query_name='customuser', 
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        blank=True,
        null=True, 
        related_name='customuser_set', 
        related_query_name='customuser', 
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # fields to be used when creating a superuser
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = "user"
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def delete(self, *args, **kwargs):
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        return super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        return super().save(*args, **kwargs)



class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification for {self.user.email}"

class EmailResetCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
       

# a model for assigning staff member users to an owner    
class Staff(models.Model):
    staff_user = models.ForeignKey(User,null=True,on_delete=models.SET_NULL,related_name='staff_user')
    owner = models.ForeignKey(User,null=True,on_delete=models.SET_NULL,related_name='staff_owner')

class Plan(models.Model):
    name = models.CharField(max_length=100,null=False,blank=False,unique=True)
    max_locations = models.IntegerField(null=False)
    max_staff = models.IntegerField(null=True)
    max_users = models.IntegerField(null=False)
    max_kds = models.IntegerField(null=False)
    kds_enabled = models.BooleanField(default=False)
    price = models.IntegerField(null=False)
    billing_cycle = models.CharField(max_length=100,choices=(('daily','daily'),('weekly','weekly'),
                                                             ('monthly','monthly'),('quarterly','quarterly'),
                                                             ('yearly','yearly')))
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)


class Owner(models.Model):
    company_owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    company_name = models.CharField(max_length=200,null=False)
    company_email = models.CharField(max_length=200,null=True)
    company_phone_number = models.CharField(max_length=200,null=True)
    company_address = models.CharField(max_length=200,null=True)
    plan = models.ForeignKey(Plan,on_delete=models.SET_NULL,null=True)
    primary_color = models.CharField(max_length=100,null=True)
    language = models.CharField(max_length=100,null=True)
    rtl_enabled = models.BooleanField(default=False)
    status = models.CharField(max_length=100,null=False,choices=(('active','active'),('trial','trial'),
                                                             ('suspended','suspended'),('cancelled','cancelled'),
                                                             ('pending','pending')))
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('company_owner','company_name')

class Subscription(models.Model):
    owner = models.ForeignKey(Owner,on_delete=models.SET_NULL,null=True)
    plan = models.ForeignKey(Plan,on_delete=models.SET_NULL,null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    billing_provider = models.CharField(max_length=100)
    status = models.CharField(max_length=100,choices=(('active','active'),('pending','pending'),('terminated','terminated')))
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('owner',)

class SubscriptionPayment(models.Model):
    subscription = models.ForeignKey(Subscription,on_delete=models.SET_NULL,null=True)
    payment_method = models.CharField(max_length=100,null=False)
    amount = models.FloatField(null=False)
    status = models.CharField(max_length=100,null=False)
    transaction_id = models.CharField(max_length=100,null=False)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)


    class Meta:
        unique_together = ["transaction_id"]



#use this model for users that have group owner, use it to store their bank accounts for payment purposes
class ZoneOwnerBankAccount(models.Model):
    owner = models.ForeignKey(Owner,null=True,on_delete=models.SET_NULL)
    account_type = models.CharField(max_length=100,null=False,choices=(('bank_account','bank_account'),('wallet','wallet'),('other','other')))
    bank_account = models.CharField(max_length=100,null=False)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = ['owner']


class ParkingZone(models.Model):
    zone_owner = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length=100,null=False)
    address = models.CharField(max_length=100,null=False)
    latitude = models.CharField(max_length=100,null=True)
    longitude = models.CharField(max_length=100,null=True)
    total_floors = models.IntegerField(null=False)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('zone_owner','name')




def validate_parking_zone_picture(value):
    valid_extensions = ['.png','.jpg','.jpeg','.PNG','.JPG','.JPEG']
    ext = os.path.splitext(value.name)[1]
    if not ext in valid_extensions:
        raise ValidationError('Unsupported filed extension')
        

def get_parking_zone_image_upload_path(instance,filename):
    new_file_name = "parking_zones/"+f'{filename}'
    return new_file_name


class ParkingZonePicture(models.Model):
    parking_zone = models.ForeignKey(ParkingZone,null=True,on_delete=models.SET_NULL)
    description = models.CharField(max_length=200,null=True)
    image = models.FileField(upload_to=get_parking_zone_image_upload_path,validators=[validate_parking_zone_picture],null=True,blank=True)



class ParkingFloor(models.Model):
    zone = models.ForeignKey(ParkingZone,on_delete=models.SET_NULL,null=True)
    floor_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('zone','floor_number')

    def __str__(self):
        return "zone - "+str(self.zone.name)+" - floor - "+str(self.floor_number)

class VehicleType(models.Model):
    name = models.CharField(max_length=100,unique=True,null=False)

class ParkingSlotGroup(models.Model):
    parking_floor = models.ForeignKey(ParkingFloor,on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=100,null=False,unique=True)


class ParkingSlot(models.Model):
    parking_slot_group = models.ForeignKey(ParkingSlotGroup,on_delete=models.SET_NULL,null=True)
    slot_number = models.CharField(max_length=100,null=False)
    is_available = models.BooleanField(default=True)
    occupied_by_booking = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('parking_slot_group','slot_number')

# a model for setting the type of cars a parking slot can accomodate
class ParkingSlot_VehicleType(models.Model):
    vehicle_type = models.ForeignKey(VehicleType,on_delete=models.SET_NULL,null=True)
    parking_slot = models.ForeignKey(ParkingFloor,on_delete=models.SET_NULL,null=True)
 


class Vehicle(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    plate_number = models.CharField(max_length=100,unique=True)
    vehicle_type = models.ForeignKey(VehicleType,on_delete=models.SET_NULL,null=True)
    rfid_tag = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('vehicle_type','user')


class PricingRule(models.Model):
    parking_zone = models.ForeignKey(ParkingZone,on_delete=models.SET_NULL,null=True)
    vehicle_type = models.ForeignKey(VehicleType,null=True,on_delete=models.SET_NULL)
    rule_name = models.CharField(max_length=100,null=True)
    rate_type = models.CharField(max_length=100,choices=(('minute','minute'),('hourly','hourly'),
                                                         ('daily','daily')))
    rate = models.FloatField(null=False)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    day_of_week = models.CharField(max_length=100,choices=(('MON','MON'),('TUE','TUE'),
                                                         ('WED','WED'),('THU','THU'),
                                                         ('FRI','FRI'),('SAT','SAT'),
                                                         ('SUN','SUN')))
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)


    class Meta:
        unique_together = ('parking_zone','vehicle_type','start_time','end_time','day_of_week')



class Booking(models.Model):
    parking_slot = models.ForeignKey(ParkingSlot,on_delete=models.SET_NULL,null=True)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.SET_NULL,null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    total_price = models.FloatField(null=False)
    status = models.CharField(max_length=100,choices=(('active','active'),('cancelled','cancelled'),('completed','completed')))
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)


class Payment(models.Model):
    booking = models.ForeignKey(Booking,on_delete=models.SET_NULL,null=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    amount = models.FloatField(null=True)
    due_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "payment"




class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    notification_type = models.CharField(max_length=100)
    #maintenance_request_id = models.ForeignKey(MaintenanceRequest,on_delete=models.SET_NULL,null=True)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True)
    booking = models.ForeignKey(Booking,on_delete=models.SET_NULL,null=True)
    message = models.CharField(max_length=200,null=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=False)
    read_at = models.DateTimeField(null=True)

class NotificationUser(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    notification = models.ForeignKey(Notification,on_delete=models.SET_NULL,null=True)

class FavoriteZones(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    parking_zone = models.ForeignKey(ParkingZone,on_delete=models.SET_NULL,null=True)


class ZoneUtitlities(models.Model):
    parking_zone = models.ForeignKey(ParkingZone,on_delete=models.SET_NULL,null=True)
    wifi = models.BooleanField(default=False)
    cctv = models.BooleanField(default=False)
    charger = models.BooleanField(default=False)




