from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User,Group,Permission,ContentType
from django.contrib.auth import get_user_model,authenticate
from rest_framework import serializers
from .models import *

User = get_user_model()

#this is a class used to customize the JWT token obtaining since we need to send the permission list to the user
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = "email"
    
    def validate(self, attrs):
        credentials={
            "email":attrs.get("email"),
            "password":attrs.get("password")
        }
    
        data = super().validate(attrs)
        user = authenticate(email=attrs['email'],password=attrs['password'])
        if user and not user.is_active:
            raise serializers.ValidationError({"error":"user is banned from the system"})
           
    

        user = authenticate(**credentials)
        
        if user is None:
            raise serializers.ValidationError({"error":"invalid credentials"})
        
        #lets add permissions to the token payload
        #permissions = user.get_all_permissions()
        data = super().validate(attrs)
        data['permissions'] = list(user.get_all_permissions())
        data['groups'] = list(user.groups.values_list('name',flat=True))
        return data
    
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    user_permissions = serializers.SlugRelatedField(slug_field="codename",queryset=Permission.objects.all(),many=True,required=False)
    groups = serializers.SlugRelatedField(slug_field="name",queryset=Group.objects.all(),many=True,required=False)
    class Meta:
        model = User
        fields = "__all__"

    def validate(self, data):
        if self.instance is None and "password" not in data:
            raise serializers.ValidationError({"password":"This field is required when creating a new user!"})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password",None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password",None)
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        """Ensure superusers receive all permissions."""
        representation = super().to_representation(instance)

        if instance.is_superuser:
            # Get all permission codenames for superusers
            all_permissions = Permission.objects.values_list("codename", flat=True)
            representation["user_permissions"] = list(all_permissions)
        else:
            # Regular users: only show explicitly assigned permissions
            representation["user_permissions"] = list(instance.user_permissions.values_list("codename", flat=True))

        return representation
    
class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(slug_field="codename",queryset=Permission.objects.all(),many=True,required=False)

    class Meta:
        model = Group
        fields = "__all__"


class PermissionSerializer(serializers.ModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField(write_only=True,queryset=ContentType.objects.all())
    class Meta:
        model = Permission
        fields = "__all__"

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = "__all__"

class ZoneOwnerBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZoneOwnerBankAccount
        fields = "__all__"
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        return representation
    
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        return representation
    
class ParkingZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingZone
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['zone_owner'] = UserSerializer(instance.zone_owner).data
        return representation
    
class ParkingFloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingFloor
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['zone'] = ParkingZoneSerializer(instance.zone).data
        return representation
    
class ParkingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['parking_floor'] = ParkingFloorSerializer(instance.parking_floor).data
        return representation
        

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['staff_user'] = UserSerializer(instance.staff_user).data
        representation['owner'] = UserSerializer(instance.owner).data
        return representation

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        #representation['booking'] = BookingSerializer(instance.booking).data
        return representation


class NotificationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationUser
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        #representation['booking'] = BookingSerializer(instance.booking).data
        return representation   