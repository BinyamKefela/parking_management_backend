from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Notification,NotificationUser
from ..serializers import NotificationSerializer
from vpms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model

MAINTENANCE_REQUEST_CREATED = "maintenance_request_created"
MAINTENANCE_REQUEST_RESOLVED = "maintenance_request_resolved"
MAINTENANCE_REQUEST_TERMINATED = 'maintenance_request_terminated'
RENT_CREATRD = "rent_created"
RENT_DUE_DATE = "rent_due_date"
RENT_TERMINATED = "rent_terminated"

User = get_user_model()

#an API for getting all the notifications of all users
class NotificationListView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = {
    #'name': ['exact', 'icontains'],
    'zone__zone_owner__email':['exact'],
    'is_read': ['exact']
    }
    search_fields = [field.name for field in Notification._meta.fields]
    ordering_fields = [field.name for field in Notification._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination


#an API for getting the notifications of a specific user
class NotificationGetUserListView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated,DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in Notification._meta.fields]
    ordering_fields = [field.name for field in Notification._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

    def get_queryset(self):
        id = self.kwargs.get('user_id')
        queryset = super().get_queryset()
        if id is not None:
            try:
                queryset = queryset.filter(user_id=User.objects.get(id=id))
                return queryset
            except:
                raise NotFound(detail="There is no notification with the given user id")
        else:
            return queryset


# an API for getting unread notifications of a specific user
class NotificationUnreadUserListView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = {
    #'name': ['exact', 'icontains'],
    'zone__zone_owner__email':['exact'],
    'is_read': ['exact']
    }
    search_fields = [field.name for field in Notification._meta.fields]
    ordering_fields = [field.name for field in Notification._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

    def get_queryset(self):
        id = self.kwargs.get('user_id')
        queryset = super().get_queryset()
        if id is not None:
            try:
               # Filter the queryset based on the primary key
               queryset = queryset.filter(user_id=User.objects.get(id=id)).exclude(id__in=NotificationUser.objects.filter(user_id=id)
                                                              .values_list("notification_id",flat=True))  # Assuming your model has an 'id' field
               return queryset
            except:
                raise NotFound(detail="There is no notification with the given ID.")
        else:
            # If no 'pk' is provided, return the default queryset (all objects)
            return queryset 




# an API for getting a specific notification
class NotificationRetrieveView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class NotificationUpdateView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class NotificationDestroyView(generics.DestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        notification = self.get_object()
        if not notification:
            return Response({"error":"notification not found!"}, status=status.HTTP_404_NOT_FOUND)
        notification.delete()
        #notification.save()
        return Response({"message":"notification deleted successfully!"},status=status.HTTP_200_OK)



class NotificationCreateView(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]