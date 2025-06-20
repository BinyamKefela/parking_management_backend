from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import ParkingZone,ParkingZone,Subscription,SubscriptionPayment
from ..serializers import ParkingZoneSerializer
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

PARKING_ZONE_INACTIVE = "inactive"
PARKING_ZONE_ACTIVE = "active"


class ParkingZoneListView(generics.ListAPIView):
    queryset = ParkingZone.objects.exclude(status=PARKING_ZONE_INACTIVE)
    serializer_class = ParkingZoneSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = {
    'name': ['exact', 'icontains'],
    'address': ['exact', 'icontains'],
    'zone_owner__email':['exact']
    }
    search_fields = ["name","address"]
    ordering_fields = [field.name for field in ParkingZone._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        today = datetime.datetime.now()
        subscription = Subscription.objects.filter(user=user,status='active').order_by('end_date').first()

        if (not SubscriptionPayment.objects.filter(subscription=subscription,subscription__end_date__gte=today,status="paid").count()>0) and (not user.is_superuser):
            queryset.delete()
        return queryset
    


class AllParkingZoneListView(generics.ListAPIView):
    queryset = ParkingZone.objects.all()
    serializer_class = ParkingZoneSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = {
    'name': ['exact', 'icontains'],
    'address': ['exact', 'icontains'],
    'zone_owner__email':['exact']
    }
    search_fields = ["name","address"]
    ordering_fields = [field.name for field in ParkingZone._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination




class ParkingZoneRetrieveView(generics.RetrieveAPIView):
    queryset = ParkingZone.objects.all()
    serializer_class = ParkingZoneSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingZoneUpdateView(generics.UpdateAPIView):
    queryset = ParkingZone.objects.all()
    serializer_class = ParkingZoneSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingZoneDestroyView(generics.DestroyAPIView):
    queryset = ParkingZone.objects.all()
    serializer_class = ParkingZoneSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        parking_zone = self.get_object()
        if not parking_zone:
            return Response({"error":"ParkingZone not found!"}, status=status.HTTP_404_NOT_FOUND)
        parking_zone.status = PARKING_ZONE_INACTIVE
        parking_zone.save()
        #ParkingZone_payment.save()
        return Response({"message":"ParkingZone deactivated successfully!"},status=status.HTTP_200_OK)


class ParkingZoneCreateView(generics.CreateAPIView):
    queryset = ParkingZone.objects.all()
    serializer_class = ParkingZoneSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def create(self, request, *args, **kwargs):
        #user_id = ParkingZone.objects.get(id=request.data.get('zone_id')).zone.zone_owner.pk
        try:
            user = User.objects.get(id=request.data.get('zone_owner'))
        except:
            return Response({"error":"there is no owner associated with the given zone id"},status=status.HTTP_404_NOT_FOUND)
        if not user.groups.filter(name="owner").exists():
            return Response({"error": "the user you are trying to create a ParkingZone for does not have a role of an owner, please assign role first."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_parking_zone(request):
    user_id = request.data.get('user')
    zone_id = request.data.get('parking_zone')

    try:
        user = User.objects.get(id=user_id)
        try:
            zone = ParkingZone.objects.get(id=zone_id,zone_owner=user)
        except:
            return Response({"error":"There is no parking zone with the given zone id and user id"},status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"error":"there is no user with the given user id"},status=status.HTTP_400_BAD_REQUEST)
    
    zone.status = PARKING_ZONE_ACTIVE
    zone.save()
    return Response({"message":"parking zone activated successfully"},status=status.HTTP_200_OK)



