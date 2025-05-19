from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import ParkingZone,ParkingZone
from ..serializers import ParkingZoneSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class ParkingZoneListView(generics.ListAPIView):
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
        ParkingZone = self.get_object()
        if not ParkingZone:
            return Response({"error":"ParkingZone not found!"}, status=status.HTTP_404_NOT_FOUND)
        ParkingZone.delete()
        #ParkingZone_payment.save()
        return Response({"message":"ParkingZone deleted successfully!"},status=status.HTTP_200_OK)


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



