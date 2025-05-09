from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import ParkingSlot_VehicleType,ParkingSlot,VehicleType
from ..serializers import ParkingSlot_VehicleTypeSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class ParkingSlot_VehicleTypeListView(generics.ListAPIView):
    queryset = ParkingSlot_VehicleType.objects.all()
    serializer_class = ParkingSlot_VehicleTypeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in ParkingSlot_VehicleType._meta.fields]
    ordering_fields = [field.name for field in ParkingSlot_VehicleType._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination



class ParkingSlot_VehicleTypeRetrieveView(generics.RetrieveAPIView):
    queryset = ParkingSlot_VehicleType.objects.all()
    serializer_class = ParkingSlot_VehicleTypeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingSlot_VehicleTypeUpdateView(generics.UpdateAPIView):
    queryset = ParkingSlot_VehicleType.objects.all()
    serializer_class = ParkingSlot_VehicleTypeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingSlot_VehicleTypeDestroyView(generics.DestroyAPIView):
    queryset = ParkingSlot_VehicleType.objects.all()
    serializer_class = ParkingSlot_VehicleTypeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        ParkingSlot_VehicleType = self.get_object()
        if not ParkingSlot_VehicleType:
            return Response({"error":"ParkingSlot_VehicleType not found!"}, status=status.HTTP_404_NOT_FOUND)
        ParkingSlot_VehicleType.delete()
        #ParkingSlot_VehicleType_payment.save()
        return Response({"message":"ParkingSlot_VehicleType deleted successfully!"},status=status.HTTP_200_OK)


class ParkingSlot_VehicleTypeCreateView(generics.CreateAPIView):
    queryset = ParkingSlot_VehicleType.objects.all()
    serializer_class = ParkingSlot_VehicleTypeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


    def create(self, request, *args, **kwargs):
        parking_zone_id = request.data.get('parking_zone')
        
        try:
            parking_slot = ParkingSlot.objects.get(pk=parking_zone_id)
        except:
            return Response({"error":"there is no parking zone with the given parking zone id"},status=status.HTTP_404_NOT_FOUND)
        return super().create(request, *args, **kwargs)
