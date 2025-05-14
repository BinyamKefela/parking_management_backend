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
  path("ativate_owner", activate_owner, name="activate_owner"),

    #---------------------------------Subscription routes-------------------------------------------------------

  path('get_subscriptions',SubscriptionListView.as_view(),name='get_subscriptions'),
  path('get_subscription/<int:id>',SubscriptionRetrieveView.as_view(),name='get_subscription'),
  path('post_subscription',SubscriptionCreateView.as_view(),name='post_subscription'),
  path('update_subscription/<int:id>',SubscriptionUpdateView.as_view(),name='update_subscription'),
  path('delete_subscription/<int:id>',SubscriptionDestroyView.as_view(),name='delete_subscription'),

      #---------------------------------Zone owner bank account routes-------------------------------------------------------

  path('get_zone_owner_bank_accounts',ZoneOwnerBankAccountListView.as_view(),name='get_zone_owner_bank_account'),
  path('get_zone_owner_bank_account/<int:id>',ZoneOwnerBankAccountRetrieveView.as_view(),name='get_zone_owner_bank_account'),
  path('post_zone_owner_bank_account',ZoneOwnerBankAccountCreateView.as_view(),name='post_zone_owner_bank_account'),
  path('update_zone_owner_bank_account/<int:id>',ZoneOwnerBankAccountUpdateView.as_view(),name='update_zone_owner_bank_account'),
  path('delete_zone_owner_bank_account/<int:id>',ZoneOwnerBankAccountDestroyView.as_view(),name='delete_zone_owner_bank_account'),


  


]