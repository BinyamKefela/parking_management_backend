from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,TokenVerifyView)
from .api.user import *
from .api.group import *
from .api.permission import *



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
  path("get_tenants",GetTenats.as_view(),name="get_tenants"),




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


  


]