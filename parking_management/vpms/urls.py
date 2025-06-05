from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,TokenVerifyView)
from .api.user import *
from .api.group import *
from .api.permission import *
from .api.plan import *
from .api.owner import *
from .api.subscription import *
from .api.zone_owner_bank_account import *
from .api.vehicle import *
from .api.vehicle_type import *
from .api.parking_zone import *
from .api.parking_zone_picture import *
from .api.parking_floor import *
from .api.parking_slot import *
from .api.parking_slot_vehicle_type import *
from .api.parking_slot_group import *
from .api.booking import *
from .api.staff import *
from .api.pricing_rule import *
from .api.default_price import *
from .api.payment import *
from .api.favorite_zones import *




urlpatterns = [
  #--------------------------------users routes-----------------------------------------------
  path("get_users", UserListView.as_view(), name="get_users"),
  path("get_user/<int:id>",UserRetrieveView.as_view(),name='get_user'),
  path("post_user",UserCreateView.as_view(),name="post_user"),
  path("update_user/<int:id>",update_user,name="new_update_user"),
  path("deactivate_user/<int:id>",UserDestroyView.as_view(),name="delete_user"),
  path("set_user_permissions",setUserPermissions,name="set_user_permissions"),
  path("set_user_groups", setUserGroups, name="set_user_group"),
  path("send_password_reset_email",send_password_reset_email,name="send_password_reset_email"),
  path("reset_password/<str:token>",reset_password,name="reset_passord"),
  path("get_user_profile",get_user_profile,name="get_user_id"),
  path("activate_user/<int:id>", activate_user, name="activate_user"),
  #path("get_owners",get_owners,name="get_owners"),
  #path("get_managers",get_managers,name="get_managers"),
  #path("get_owners",GetOwners.as_view(),name="get_owners"),

  path('sign_up',sign_up, name='sign_up'),
  path('verify-email/<uuid:token>', verify_email, name='verify_email'),

  path('send_password_reset_email_phone',send_password_reset_email_phone, name='send_password_reset_email_phone'),
  path('verify_reset_code', VerifyResetCodeView.as_view(), name='verify_reset_code'),
  path('reset_password_phone',reset_password_phone,name='reset_password_phone'),

  path("change_password",change_password,name="change_password"),





    #--------------------------------Groups routes----------------------------------------------
  path("get_groups", GroupListView.as_view(), name="get_groups"),
  path("get_group/<int:id>",GroupRetrieveView.as_view(),name='get_group'),
  path("post_group",GroupCreateView.as_view(),name="post_group"),
  path("update_group/<int:id>",GroupUpdateView.as_view(),name="update_group"),
  path("delete_group/<int:id>",GroupDestroyView.as_view(),name="delete_group"),
  path("set_group_permissions",setGroupPermissions,name="set_group_permissions"),
  path("get_group_permissions",getGroupPermission,name="get_group_permissions"),



    #--------------------------------Permission routes--------------------------------------------
  path("get_permissions", PermissionListView.as_view(), name="get_permissions"),
  path("get_permission/<int:id>",PermissionRetrieveView.as_view(),name='get_permission'),
  path("post_permission",PermissionCreateView.as_view(),name="post_permission"),
  path("update_permission/<int:id>",PermissionUpdateView.as_view(),name="update_permission"),
  path("delete_permission/<int:id>",PermissionDestroyView.as_view(),name="delete_permission"),
  

  #---------------------------------Plan routes-------------------------------------------------------

  path('get_plans',PlanListView.as_view(),name='get_plans'),
  path('get_plan/<int:id>',PlanRetrieveView.as_view(),name='get_plan'),
  path('post_plan',PlanCreateView.as_view(),name='post_plan'),
  path('update_plan/<int:id>',PlanUpdateView.as_view(),name='update_plan'),
  path('delete_plan/<int:id>',PlanDestroyView.as_view(),name='delete_plan'),


  #---------------------------------Owner routes-------------------------------------------------------

  path('get_owners',OwnerListView.as_view(),name='get_owners'),
  path('get_owner/<int:id>',OwnerRetrieveView.as_view(),name='get_owner'),
  path('post_owner',OwnerCreateView.as_view(),name='post_owner'),
  path('update_owner/<int:id>',OwnerUpdateView.as_view(),name='update_owner'),
  path('delete_owner/<int:id>',OwnerDestroyView.as_view(),name='delete_owner'),
  path("activate_owner", activate_owner, name="activate_owner"),

    #---------------------------------Subscription routes-------------------------------------------------------

  path('get_subscriptions',SubscriptionListView.as_view(),name='get_subscriptions'),
  path('get_subscription/<int:id>',SubscriptionRetrieveView.as_view(),name='get_subscription'),
  path('post_subscription',SubscriptionCreateView.as_view(),name='post_subscription'),
  path('update_subscription/<int:id>',SubscriptionUpdateView.as_view(),name='update_subscription'),
  path('delete_subscription/<int:id>',SubscriptionDestroyView.as_view(),name='delete_subscription'),

      #---------------------------------Zone owner bank account routes-------------------------------------------------------

  path('get_zone_owner_bank_accounts',ZoneOwnerBankAccountListView.as_view(),name='get_zone_owner_bank_accounts'),
  path('get_zone_owner_bank_account/<int:id>',ZoneOwnerBankAccountRetrieveView.as_view(),name='get_zone_owner_bank_account'),
  path('post_zone_owner_bank_account',ZoneOwnerBankAccountCreateView.as_view(),name='post_zone_owner_bank_account'),
  path('update_zone_owner_bank_account/<int:id>',ZoneOwnerBankAccountUpdateView.as_view(),name='update_zone_owner_bank_account'),
  path('delete_zone_owner_bank_account/<int:id>',ZoneOwnerBankAccountDestroyView.as_view(),name='delete_zone_owner_bank_account'),


#---------------------------------vehicle type routes-------------------------------------------------------

  path('get_vehicle_types',VehicleTypeListView.as_view(),name='get_vehicle_types'),
  path('get_vehicle_type/<int:id>',VehicleTypeRetrieveView.as_view(),name='get_vehicle_type'),
  path('post_vehicle_type',VehicleTypeCreateView.as_view(),name='post_vehicle_type'),
  path('update_vehicle_type/<int:id>',VehicleTypeUpdateView.as_view(),name='update_vehicle_type'),
  path('delete_vehicle_type/<int:id>',VehicleTypeDestroyView.as_view(),name='delete_vehicle_type'),



#---------------------------------vehicle routes-------------------------------------------------------

  path('get_vehicles',VehicleListView.as_view(),name='get_vehicle'),
  path('get_vehicle/<int:id>',VehicleRetrieveView.as_view(),name='get_vehicle'),
  path('post_vehicle',VehicleCreateView.as_view(),name='post_vehicle'),
  path('update_vehicle/<int:id>',VehicleUpdateView.as_view(),name='update_vehicle'),
  path('delete_vehicle/<int:id>',VehicleDestroyView.as_view(),name='delete_vehicle'),



  #---------------------------------Parking zone routes-------------------------------------------------------

  path('get_parking_zones',ParkingZoneListView.as_view(),name='get_parking_zones'),
  path('get_all_parking_zones',AllParkingZoneListView.as_view(),name='get_parking_zones'),
  path('get_parking_zone/<int:id>',ParkingZoneRetrieveView.as_view(),name='get_parking_zone'),
  path('post_parking_zone',ParkingZoneCreateView.as_view(),name='post_parking_zone'),
  path('update_parking_zone/<int:id>',ParkingZoneUpdateView.as_view(),name='update_parking_zone'),
  path('delete_parking_zone/<int:id>',ParkingZoneDestroyView.as_view(),name='delete_parking_zone'),
  path('activate_parking_zone',activate_parking_zone,name='activate_parking_zone'),


  #---------------------------------Parking zone picture routes-------------------------------------------------------

  path('get_parking_zone_pictures',ParkingZonePictureListView.as_view(),name='get_parking_zone_pictures'),
  path('get_parking_zone_picture/<int:id>',ParkingZonePictureRetrieveView.as_view(),name='get_parking_zone_picture'),
  path('post_parking_zone_picture',ParkingZonePictureCreateView.as_view(),name='post_parking_zone'),
  path('update_parking_zone_picture/<int:id>',ParkingZonePictureUpdateView.as_view(),name='update_parking_zone_picture'),
  path('delete_parking_zone_picture/<int:id>',ParkingZonePictureDestroyView.as_view(),name='delete_parking_zone_picture'),


      #---------------------------------Parking floor routes-------------------------------------------------------

  path('get_parking_floors',ParkingFloorListView.as_view(),name='get_parking_floors'),
  path('get_parking_floor/<int:id>',ParkingFloorRetrieveView.as_view(),name='get_parking_floor'),
  path('post_parking_floor',ParkingFloorCreateView.as_view(),name='post_parking_floor'),
  path('update_parking_floor/<int:id>',ParkingFloorUpdateView.as_view(),name='update_parking_floor'),
  path('delete_parking_floor/<int:id>',ParkingFloorDestroyView.as_view(),name='delete_parking_floor'),


   #---------------------------------Parking slot vehicle type routes-------------------------------------------------------

  path('get_parking_slot_vehicle_types',ParkingSlot_VehicleTypeListView.as_view(),name='get_parking_slot_vehicle_types'),
  path('get_parking_slot_vehicle_type/<int:id>',ParkingSlot_VehicleTypeRetrieveView.as_view(),name='get_parking_slot_vehicle_type'),
  path('post_parking_slot_vehicle_type',ParkingSlot_VehicleTypeCreateView.as_view(),name='post_parking_slot_vehicle_type'),
  path('update_parking_slot_vehicle_type/<int:id>',ParkingSlot_VehicleTypeUpdateView.as_view(),name='update_parking_slot_vehicle_type'),
  path('delete_parking_slot_vehicle_type/<int:id>',ParkingSlot_VehicleTypeDestroyView.as_view(),name='delete_parking_slot_vehicle_type'),



  #---------------------------------Parking slot routes-------------------------------------------------------

  path('get_parking_slots',ParkingSlotListView.as_view(),name='get_parking_slots'),
  path('get_parking_slot/<int:id>',ParkingSlotRetrieveView.as_view(),name='get_parking_slot'),
  path('post_parking_slot',ParkingSlotCreateView.as_view(),name='post_parking_slot'),
  path('update_parking_slot/<int:id>',ParkingSlotUpdateView.as_view(),name='update_parking_slot'),
  path('delete_parking_slot/<int:id>',ParkingSlotDestroyView.as_view(),name='delete_parking_slot'),



   #---------------------------------Parking slot group routes-------------------------------------------------------

  path('get_parking_slot_groups',ParkingSlotGroupListView.as_view(),name='get_parking_slot_groups'),
  path('get_parking_slot_group/<int:id>',ParkingSlotGroupRetrieveView.as_view(),name='get_parking_slot_group'),
  path('post_parking_slot_group',ParkingSlotGroupCreateView.as_view(),name='post_parking_slot_group'),
  path('update_parking_slot_group/<int:id>',ParkingSlotGroupUpdateView.as_view(),name='update_parking_slot_group'),
  path('delete_parking_slot_group/<int:id>',ParkingSlotGroupDestroyView.as_view(),name='delete_parking_slot_group'),



     #---------------------------------booking routes-------------------------------------------------------

  path('get_bookings',BookingListView.as_view(),name='get_bookings'),
  path('get_booking/<int:id>',BookingRetrieveView.as_view(),name='get_booking'),
  path('post_booking',BookingCreateView.as_view(),name='post_booking'),
  path('update_booking/<int:id>',BookingUpdateView.as_view(),name='update_booking'),
  path('delete_booking/<int:id>',BookingDestroyView.as_view(),name='delete_booking'),
  path('cancel_booking',cancel_booking,name="cancel_booking"),
  path('cancel_booking_phone/<str:booking>',cancel_booking_phone,name="cancel_booking_phone"),

  path('calculate_price', CalculatePriceView.as_view(), name='calculate_price'),
  path('make_payment',make_payment,name="make_payment"),
  path('make_payment_phone/<str:booking>/<str:end_time>',make_payment_phone,name="make_payment_phone"),
  

  
  #---------------------------------staff routes-------------------------------------------------------

  path('get_staffs',StaffListView.as_view(),name='get_staffs'),
  path('get_staff/<int:id>',StaffRetrieveView.as_view(),name='get_staff'),
  path('post_staff',create_staff,name='post_staff'),
  path('update_staff/<int:id>',StaffUpdateView.as_view(),name='update_staff'),
  path('delete_staff/<int:id>',StaffDestroyView.as_view(),name='delete_staff'),



#------------------------------------pricing rules------------------------------------------------------

  path('get_pricing_rules',PricingRuleListView.as_view(),name='get_pricing_rules'),
  path('get_pricing_rule/<int:id>',PricingRuleRetrieveView.as_view(),name='get_pricing_rule'),
  path('post_pricing_rule',PricingRuleCreateView.as_view(),name='post_pricing_rule'),
  path('update_pricing_rule/<int:id>',PricingRuleUpdateView.as_view(),name='update_pricing_rule'),
  path('delete_pricing_rule/<int:id>',PricingRuleDestroyView.as_view(),name='delete_pricing_rule'),
  

#------------------------------------default price------------------------------------------------------

  path('get_default_prices',DefaultPriceListView.as_view(),name='get_default_prices'),
  path('get_default_price/<int:id>',DefaultPriceRetrieveView.as_view(),name='get_default_price'),
  path('post_default_price',DefaultPriceCreateView.as_view(),name='post_default_price'),
  path('update_default_price/<int:id>',DefaultPriceUpdateView.as_view(),name='update_default_price'),
  path('delete_default_price/<int:id>',DefaultPriceDestroyView.as_view(),name='delete_default_price'),


#------------------------------------payment------------------------------------------------------

  path('get_payments',PaymentListView.as_view(),name='get_payments'),
  path('get_payment/<int:id>',PaymentRetrieveView.as_view(),name='get_payment'),
  path('post_payment',PaymentCreateView.as_view(),name='post_payment'),
  path('update_payment/<int:id>',PaymentUpdateView.as_view(),name='update_payment'),
  path('delete_payment/<int:id>',PaymentDestroyView.as_view(),name='delete_payment'),




#------------------------------------favorite zones------------------------------------------------------

  path('get_favorite_zones',FavoriteZonesListView.as_view(),name='get_favorite_zones'),
  path('get_favorite_zone/<int:id>',FavoriteZonesRetrieveView.as_view(),name='get_favorite_zone'),
  path('post_favorite_zone',FavoriteZonesCreateView.as_view(),name='post_favorite_zone'),
  path('update_favorite_zone/<int:id>',FavoriteZonesUpdateView.as_view(),name='update_favorite_zone'),
  path('delete_favorite_zone/<int:id>',FavoriteZonesDestroyView.as_view(),name='delete_favorite_zone'),
  

]