from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Booking,ParkingZone,ParkingSlot,Vehicle,ParkingSlot_VehicleType,DefaultPrice
from ..serializers import BookingSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view,permission_classes



User = get_user_model()

BOOKING_ACTIVE = "active"
BOOKING_CANCELLED = "cancelled"
BOOKING_COMPLETE = "completeed"


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
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request):
    booking_id = request.data.get("booking_id")
    try:
        booking = Booking.objects.get(id=booking_id)
        if not (booking.status == BOOKING_ACTIVE):
            return Response({"there is no active booking with the given booking id"},status=status.HTTP_400_BAD_REQUEST)
        booking.status = BOOKING_CANCELLED
        booking.save()
        return Response({"message","Booking cancelled successfully"},status=status.HTTP_200_OK)
    except:
        return Response({"error":"There is no booking with the given booking id"},status=status.HTTP_400_BAD_REQUEST)
    



# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils.timezone import make_aware
from vpms.models import PricingRule, ParkingZone, VehicleType
from vpms.serializers import PricingCalculationSerializer


#an API for returnng the price of a slot based on pricing rules provided
from datetime import timedelta
from django.utils.timezone import make_aware, is_naive
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


def get_default_rate(parking_zone):
    try:
        rule = DefaultPrice.objects.get(
            parking_zone=parking_zone,
        )
        return rule.rate
    except DefaultPrice.DoesNotExist:
        return 0  


class CalculatePriceView(APIView):
    def post(self, request):
        serializer = PricingCalculationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        zone_id = data['parking_zone']
        vehicle_type_id = data['vehicle_type']
        start = data['start_datetime']
        end = data['end_datetime']

        if start >= end:
            return Response({"error": "End time must be after start time."}, status=400)

        if is_naive(start):
            start = make_aware(start)
        if is_naive(end):
            end = make_aware(end)

        total_price = 0.0
        current = start

        while current < end:
            day = current.strftime("%a").upper()[:3]  # e.g., MON
            current_time = current.time()

            rules = PricingRule.objects.filter(
                parking_zone_id=zone_id,
                vehicle_type_id=vehicle_type_id,
                day_of_week=day,
                start_time__lte=current_time,
                end_time__gte=current_time,
                is_enabled=True
            )

            if rules.exists():
                rule = rules.first()
                if rule.rate_type == 'minute':
                    total_price += rule.rate
                elif rule.rate_type == 'hourly':
                    total_price += rule.rate / 60
                elif rule.rate_type == 'daily':
                    total_price += rule.rate / (24 * 60)
            else:
                # Fallback to default daily rate, distributed per minute
                total_price += get_default_rate(parking_zone=zone_id)

            current += timedelta(minutes=1)

        return Response({
            "total_price": round(total_price, 2),
            "start_time": start,
            "end_time": end
        }, status=200)
