from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Booking,ParkingZone,ParkingSlot,Vehicle,ParkingSlot_VehicleType,DefaultPrice,Payment
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
BOOKING_COMPLETE = "completed"
ALL_VEHICLE_TYPES = "all"


class BookingListView(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    #filterset_fields = '__all__'
    #search_fields = [field.name for field in Booking._meta.fields]
    filterset_fields = {
    #'name': ['exact', 'icontains'],
    'parking_slot__slot_number':['exact'],
    'vehicle__plate_number': ['exact','icontains'],
    'vehicle_number':['exact','icontains'],
    'status':['exact','icontains'],
    'parking_slot__parking_slot_group__parking_floor__zone__zone_owner__email':['exact',]
    }
    search_fields = ["parking_slot__slot_number","vehicle__plate_number","vehicle_number"]

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
        vehicle_number = request.data.get("vehicle_number")
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")
        total_price = request.data.get('total_price')
        try:
            parking_slot = ParkingSlot.objects.get(id=parking_slot_id)
            if parking_slot.is_available == False:
                return Response({"error":"The selected parking slot is currently unavailable"},status=403)
        except:
            return Response({"error":"There is no parking slot with the given parking slot"},status=400)
        
        try:
            if vehicle_id:
                vehicle = Vehicle.objects.get(id=vehicle_id)
                vehicle_type = vehicle.vehicle_type
            else: vehicle_type = VehicleType.objects.get(name=ALL_VEHICLE_TYPES)
        except:
            return Response({"error":"There is no vehicle with the given vehicle id"},status=403)
        
        #checking the selected vehicle can be parked in the given parking slot
        if vehicle_type and ((not ParkingSlot_VehicleType.objects.filter(parking_slot=parking_slot,vehicle_type=vehicle_type).count() > 0)):
            if not vehicle_number:
              if not vehicle.vehicle_type.name == ALL_VEHICLE_TYPES:
        #if (vehicle_type or vehicle_id==None) and (not (ParkingSlot_VehicleType.objects.filter(parking_slot=parking_slot,vehicle_type=vehicle_type).count() > 0 or ParkingSlot_VehicleType.objects.filter(parking_slot=parking_slot,vehicle_type__name=ALL_VEHICLE_TYPES))):
                   return Response({"error":"The selected vehicle can't be parked in the selected parking slot"},status=403)
        booking =  Booking()
        booking.parking_slot = parking_slot
        if vehicle_id:
            booking.vehicle = vehicle
        booking.start_time = start_time
        if end_time:
            booking.end_time = end_time
        booking.status = BOOKING_ACTIVE
        if total_price:
            booking.total_price = total_price
        if vehicle_number:
            booking.vehicle_number = vehicle_number
        if total_price:
            parking_slot.is_available = False
        booking.save()
        parking_slot.is_available=False
        parking_slot.save()
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request):
    booking_id = request.data.get("booking")
    try:
        booking = Booking.objects.get(id=booking_id)
        if not (booking.status == BOOKING_ACTIVE):
            return Response({"there is no active booking with the given booking id"},status=status.HTTP_400_BAD_REQUEST)
        parking_slot = booking.parking_slot
        parking_slot.is_available = True
        booking.status = BOOKING_CANCELLED
        parking_slot.save()
        booking.save()
        return Response({"message","Booking cancelled successfully"},status=status.HTTP_200_OK)
    except:
        return Response({"error":"There is no booking with the given booking id"},status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking_phone(request,booking):
    booking_id = booking
    try:
        booking = Booking.objects.get(id=booking_id)
        if not (booking.status == BOOKING_ACTIVE):
            return Response({"there is no active booking with the given booking id"},status=status.HTTP_400_BAD_REQUEST)
        parking_slot = booking.parking_slot
        parking_slot.is_available = True
        booking.status = BOOKING_CANCELLED
        parking_slot.save()
        booking.save()
        return Response({"message","Booking cancelled successfully"},status=status.HTTP_200_OK)
    except:
        return Response({"error":"There is no booking with the given booking id"},status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request):
    booking_id = request.data.get("booking")
    end_time = request.data.get("end_time")
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.end_time = end_time
        booking.total_price = calculate_price(parking_zone=booking.parking_slot.parking_slot_group.parking_floor.zone,start_time=booking.start_time,end_time=end_time)
        booking.status=BOOKING_COMPLETE
        try:
            parking_slot = ParkingSlot.objects.get(id=booking.parking_slot.id)
            parking_slot.is_available=True
            payment = Payment()
            payment.booking = booking
            payment.user = request.user
            payment.amount = booking.total_price
            payment.status = "complete"
            payment.created_at = datetime.datetime.now()
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_404_NOT_FOUND)
    except Exception as ex:
        return Response({"error":"Ther is no booking with the given booking id"},status=status.HTTP_404_NOT_FOUND)
    booking.save()
    parking_slot.save()
    payment.save()
    return Response({"message":"payment completed successfully"},status=status.HTTP_200_OK)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def make_payment_phone(request,booking,end_time):
    booking_id = booking
    end_time = end_time
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.end_time = end_time
        booking.total_price = calculate_price(parking_zone=booking.parking_slot.parking_slot_group.parking_floor.zone,start_time=booking.start_time,end_time=end_time)
        booking.status=BOOKING_COMPLETE
        try:
            parking_slot = ParkingSlot.objects.get(id=booking.parking_slot.id)
            parking_slot.is_available=True
            payment = Payment()
            payment.booking = booking
            payment.user = request.user
            payment.amount = booking.total_price
            payment.status = "complete"
            payment.created_at = datetime.datetime.now()
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_404_NOT_FOUND)
    except Exception as ex:
        return Response({"error":"Ther is no booking with the given booking id"},status=status.HTTP_404_NOT_FOUND)
    booking.save()
    parking_slot.save()
    payment.save()
    return Response({"message":"payment completed successfully"},status=status.HTTP_200_OK)



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
            parking_zone=parking_zone
        )
        return rule.rate
    except DefaultPrice.DoesNotExist:
        return 0  

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import is_naive, make_aware
from datetime import timedelta




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

        # Ensure timezone-aware datetimes
        if is_naive(start):
            start = make_aware(start)
        if is_naive(end):
            end = make_aware(end)

        total_price = 0.0
        current = start

        # Load all relevant pricing rules once
        rules = PricingRule.objects.filter(
            parking_zone_id=zone_id,
            vehicle_type_id=vehicle_type_id,
            is_enabled=True
        ).order_by('start_time')

        # Group rules by day for fast lookup
        rules_by_day = {day: [] for day in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']}
        for rule in rules:
            rules_by_day[rule.day_of_week].append(rule)

        # Cache default rate once per request
        default_rate_per_minute = get_default_rate(parking_zone=zone_id)

        # Minute-by-minute billing loop, now using in-memory rule lookup
        while current < end:
            day = current.strftime("%a").upper()[:3]  # e.g., MON
            current_time = current.time()

            matched_rule = next(
                (r for r in rules_by_day.get(day, [])
                 if r.start_time <= current_time <= r.end_time),
                None
            )

            if matched_rule:
                if matched_rule.rate_type == 'minute':
                    total_price += matched_rule.rate
                elif matched_rule.rate_type == 'hourly':
                    total_price += matched_rule.rate / 60
                elif matched_rule.rate_type == 'daily':
                    total_price += matched_rule.rate / (24 * 60)
            else:
                total_price += default_rate_per_minute

            current += timedelta(minutes=1)

        return Response({
            "total_price": round(total_price, 2),
            "start_time": start,
            "end_time": end
        }, status=200)

    


def calculate_price(parking_zone,start_time,end_time):
    #serializer = PricingCalculationSerializer(data=request.data)
    #if not serializer.is_valid():
    #    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #data = serializer.validated_data
    zone_id = parking_zone
    start = start_time
    end = end_time
    if isinstance(start_time, str):
        start = datetime.datetime.fromisoformat(start_time)
    else:
        start = start_time

    if isinstance(end_time, str):
        end = datetime.datetime.fromisoformat(end_time)
    else:
        end = end_time

    if is_naive(start):
        start = make_aware(start)
    if is_naive(end):
        end = make_aware(end)

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
    
    return  round(total_price, 2)
            