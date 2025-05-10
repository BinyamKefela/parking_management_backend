from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Booking,ParkingZone,ParkingSlot,Vehicle,ParkingSlot_VehicleType,VehicleType
from ..serializers import BookingSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()

BOOKING_ACTIVE = "active"
BOOKING_CANCELLED = "cancelled"
BOOKING_COMPLETE = "complete"


class BookingListView(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in Booking._meta.fields]
    ordering_fields = [field.name for field in Booking._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination



class BookingRetrieveView(generics.RetrieveAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class BookingUpdateView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class BookingDestroyView(generics.DestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        Booking = self.get_object()
        if not Booking:
            return Response({"error":"Booking not found!"}, status=status.HTTP_404_NOT_FOUND)
        Booking.delete()
        #Booking_payment.save()
        return Response({"message":"Booking deleted successfully!"},status=status.HTTP_200_OK)


class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


    def create(self, request, *args, **kwargs):
        parking_slot_id = request.data.get("parking_slot")
        vehicle_id = request.data.get("vehicle")
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")
        try:
            parking_slot = ParkingSlot.objects.get(id=parking_slot_id)
            if parking_slot.is_available == False:
                return Response({"error":"The selected parking slot is currently unavailable"},status=403)
        except:
            return Response({"error":"There is no parking slot with the given parking slot"},status=400)
        
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            vehicle_type = vehicle.vehicle_type
        except:
            return Response({"error":"There is no vehicle with the given vehicle id"},status=403)
        
        #checking the selected vehicle can be parked in the given parking slot
        if vehicle_type and not (ParkingSlot_VehicleType.objects.filter(parking_slot=parking_slot,VehicleType=vehicle_type).count() > 0):
            return Response({"error":"The selected vehicle can't be parked in the selected parking slot"},status=403)
        booking =  Booking()
        booking.parking_slot = parking_slot
        booking.vehicle = vehicle
        booking.start_time = start_time
        booking.end_time = end_time
        booking.status = BOOKING_ACTIVE

        parking_slot.is_available = False
        booking.save()
        parking_slot.save()
        return super().create(request, *args, **kwargs)