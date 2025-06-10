from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import ZoneUtilities,ParkingSlot,VehicleType,ParkingZone
from ..serializers import ZoneUtilitiesSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class ZoneUtilitiesListView(generics.ListAPIView):
    queryset = ZoneUtilities.objects.all()
    serializer_class = ZoneUtilitiesSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    #filterset_fields = '__all__'
    #search_fields = [field.name for field in ZoneUtilities._meta.fields]
    filterset_fields = {
    #'name': ['exact', 'icontains'],
    'parking_zone__zone_owner__email':['exact'],
    'parking_zone__id':['exact'],
    
    }
    search_fields = ["parking_zone__zone_owner__email","rule_name","rate","vehicle_type__name"]
    ordering_fields = [field.name for field in ZoneUtilities._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination



class ZoneUtilitiesRetrieveView(generics.RetrieveAPIView):
    queryset = ZoneUtilities.objects.all()
    serializer_class = ZoneUtilitiesSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ZoneUtilitiesUpdateView(generics.UpdateAPIView):
    queryset = ZoneUtilities.objects.all()
    serializer_class = ZoneUtilitiesSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ZoneUtilitiesDestroyView(generics.DestroyAPIView):
    queryset = ZoneUtilities.objects.all()
    serializer_class = ZoneUtilitiesSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        ZoneUtilities = self.get_object()
        if not ZoneUtilities:
            return Response({"error":"ZoneUtilities not found!"}, status=status.HTTP_404_NOT_FOUND)
        ZoneUtilities.delete()
        #ZoneUtilities_payment.save()
        return Response({"message":"ZoneUtilities deleted successfully!"},status=status.HTTP_200_OK)


class ZoneUtilitiesCreateView(generics.CreateAPIView):
    queryset = ZoneUtilities.objects.all()
    serializer_class = ZoneUtilitiesSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


    
