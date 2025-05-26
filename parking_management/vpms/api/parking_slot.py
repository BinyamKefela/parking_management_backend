from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import ParkingSlot,ParkingSlotGroup
from ..serializers import ParkingSlotSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class ParkingSlotListView(generics.ListAPIView):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    #filterset_fields = '__all__'
    #search_fields = [field.name for field in ParkingSlot._meta.fields]
    filterset_fields = {
    #'name': ['exact', 'icontains'],
    'parking_slot_group__parking_floor__zone__zone_owner__id':['exact'],
    'parking_slot_group__name': ['exact','icontains'],
    'slot_number':['exact'],
    'occupied_by_booking':['exact','icontains']
    }
    search_fields = ["parking_slot_group__name","slot_number","occupied_by_booking"]
    ordering_fields = [field.name for field in ParkingSlot._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination





class ParkingSlotRetrieveView(generics.RetrieveAPIView):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingSlotUpdateView(generics.UpdateAPIView):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingSlotDestroyView(generics.DestroyAPIView):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        ParkingSlot = self.get_object()
        if not ParkingSlot:
            return Response({"error":"ParkingSlot not found!"}, status=status.HTTP_404_NOT_FOUND)
        ParkingSlot.delete()
        #ParkingSlot_payment.save()
        return Response({"message":"ParkingSlot deleted successfully!"},status=status.HTTP_200_OK)


class ParkingSlotCreateView(generics.CreateAPIView):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def create(self, request, *args, **kwargs):
        try:
            parking_slot_group = ParkingSlotGroup.objects.get(id=request.data.get('parking_slot_group'))
        except:
            return Response({"error":"there is no parking slot group with the given parking slot group id"},status=status.HTTP_400_BAD_REQUEST)
        #checking whether there is a user for the parking slot's parking floor's parking slot
        
        #checking whether there is an owner for the parking slot's parking floor's parking slot
        
        return super().create(request, *args, **kwargs)



