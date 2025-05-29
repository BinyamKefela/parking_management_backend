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
    profile_picture = serializers.SerializerMethodField()
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
    
    def get_profile_picture(self,obj):
        request = self.context.get('request')
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        elif obj.profile_picture:
            # fallback if no request is available
            from django.conf import settings
            return settings.SITE_URL + obj.profile_picture.url
        return None
    
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

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['company_owner'] = UserSerializer(instance.company_owner).data
        representation['plan'] = PlanSerializer(instance.plan).data
        return representation
    
class ZoneOwnerBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZoneOwnerBankAccount
        fields = "__all__"
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['owner'] = OwnerSerializer(instance.owner).data
        return representation
    
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['owner'] = OwnerSerializer(instance.owner).data
        representation['plan'] = PlanSerializer(instance.plan).data if instance.plan else None
        return representation
    
class ParkingZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingZone
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['zone_owner'] = UserSerializer(instance.zone_owner).data
        representation["parking_floors"] = ParkingFloorSerializer(ParkingFloor.objects.filter(zone=instance.id),many=True).data
        representation['parking_zone_pictures'] = ParkingZonePictureSerializerDummy(ParkingZonePicture.objects.filter(parking_zone=instance.id),many=True).data
        return representation
    
class ParkingZoneSerializerDummy(serializers.ModelSerializer):
    class Meta:
        model = ParkingZone
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        #representation['zone_owner'] = UserSerializer(instance.zone_owner).data
        representation["parking_floors"] = ParkingFloorSerializerDummy(ParkingFloor.objects.filter(zone=instance.id),many=True).data
        return representation
    
    
    

class ParkingZonePictureSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = ParkingZonePicture
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            request = self.context.get('request')
            if request:
                representation['image'] = request.build_absolute_uri(instance.image.url)
            else:
                from django.conf import settings
                representation['image'] = settings.SITE_URL + instance.image.url
        else:
            representation['image'] = None
        representation['parking_zone'] = ParkingZoneSerializer(instance.parking_zone).data
        return representation



class ParkingZonePictureSerializerDummy(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = ParkingZonePicture
        fields = "__all__"
    def get_image(self,obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            # fallback if no request is available
            from django.conf import settings
            return settings.SITE_URL + obj.image.url
        return None

    
    
    
class ParkingFloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingFloor
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['zone'] = ParkingZoneSerializerDummy(instance.zone).data
        representation['parking_slot_groups'] = ParkingSlotGroupSerializerDummyDummy(ParkingSlotGroup.objects.filter(parking_floor=instance.id),many=True).data
        return representation
    

class ParkingFloorSerializerDummy(serializers.ModelSerializer):
    class Meta:
        model = ParkingFloor
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        #representation['zone'] = ParkingZoneSerializerDummy(instance.zone).data
        representation['parking_slot_groups'] = ParkingSlotGroupSerializerDummy(ParkingSlotGroup.objects.filter(parking_floor=instance.id),many=True).data
        return representation
    
class ParkingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        representation['parking_slot_vehicle_types'] = ParkingSlot_VehicleTypeSerializerDummy(ParkingSlot_VehicleType.objects.filter(parking_slot=instance.id),many=True).data
        return representation
    

class ParkingSlotSerializerDummy(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['parking_slot_groups'] = ParkingSlotGroupSerializerDummyDummy(ParkingSlot.objects.filter(id=instance.parking_slot_group),many=True).data
        #representation['parking_slot_group'] = ParkingSlotGroupSerializerDummy(instance.parking_slot_group).data
        representation['parking_slot_vehicle_types'] = ParkingSlot_VehicleTypeSerializerDummy(ParkingSlot_VehicleType.objects.filter(parking_slot=instance.id),many=True).data
        return representation


  
class ParkingSlotGroupSerializerDummy(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlotGroup
        fields = "__all__"

    def to_representation(self, instance):
       representation = super().to_representation(instance)
       representation['parking_slots'] = ParkingSlotSerializer(ParkingSlot.objects.filter(parking_slot_group=instance.id),many=True).data

       return representation

  
class ParkingSlotGroupSerializerDummyDummy(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlotGroup
        fields = "__all__"

    def to_representation(self, instance):
       representation = super().to_representation(instance)
       representation['parking_slots'] = ParkingSlotSerializer(ParkingSlot.objects.filter(parking_slot_group=instance.id),many=True).data

       return representation

   
class ParkingSlotGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlotGroup
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['parking_floor'] = ParkingFloorSerializer(instance.parking_floor).data
        representation['parking_slots'] = ParkingSlotSerializer(ParkingSlot.objects.filter(parking_slot_group=instance.id),many=True).data

        return representation
        

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['staff_user'] = UserSerializer(instance.staff_user).data
        representation['owner'] = UserSerializer(instance.owner).data
        return representation

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = "__all__"

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        #representation['booking'] = BookingSerializer(instance.booking).data
        return representation


class NotificationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationUser
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        #representation['booking'] = BookingSerializer(instance.booking).data
        return representation

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance) 
        representation['user'] = UserSerializer(instance.user).data
        return representation
    
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance) 
        representation['parking_slot'] = ParkingSlotSerializer(instance.parking_slot).data
        representation['vehicle'] = VehicleSerializer(instance.vehicle).data
        return representation
    

class ParkingSlot_VehicleTypeSerializerDummy(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot_VehicleType
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance) 
        #representation['parking_slot'] = ParkingSlotGroupSerializerDummy(instance.parking_slot).data
        representation['vehicle_type'] = VehicleTypeSerializer(instance.vehicle_type).data
        return representation

class ParkingSlot_VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot_VehicleType
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance) 
        representation['parking_slot'] = ParkingSlotSerializer(instance.parking_slot).data
        representation['vehicle_type'] = VehicleTypeSerializer(instance.vehicle_type).data
        return representation
    
class PricingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingRule
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance) 
        representation['parking_zone'] = ParkingZoneSerializer(instance.parking_zone).data
        representation['vehicle_type'] = VehicleTypeSerializer(instance.vehicle_type).data
        return representation
    
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance) 
        representation['parking_slot'] = ParkingSlotSerializer(instance.parking_slot).data
        representation['vehicle'] = VehicleSerializer(instance.vehicle).data
        return representation
    




class PricingCalculationSerializer(serializers.Serializer):
    parking_zone = serializers.IntegerField()
    vehicle_type = serializers.IntegerField()
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()


class DefaultPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultPrice
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"



