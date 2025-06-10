from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import FavoriteZones
from ..serializers import FavoriteZonesSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from vpms.models import ParkingZone


User = get_user_model()


class FavoriteZonesListView(generics.ListAPIView):
    queryset = FavoriteZones.objects.all()
    serializer_class = FavoriteZonesSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    #filterset_fields = '__all__'
    #search_fields = [field.name for field in FavoriteZones._meta.fields]
    filterset_fields = {
    'user__id': ['exact',],
    }
    search_fields = ["user__email","user_id","parking_zone__name"]
    ordering_fields = [field.name for field in FavoriteZones._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination





class FavoriteZonesRetrieveView(generics.RetrieveAPIView):
    queryset = FavoriteZones.objects.all()
    serializer_class = FavoriteZonesSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class FavoriteZonesUpdateView(generics.UpdateAPIView):
    queryset = FavoriteZones.objects.all()
    serializer_class = FavoriteZonesSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class FavoriteZonesDestroyView(generics.DestroyAPIView):
    queryset = FavoriteZones.objects.all()
    serializer_class = FavoriteZonesSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        FavoriteZones = self.get_object()
        if not FavoriteZones:
            return Response({"error":"FavoriteZones not found!"}, status=status.HTTP_404_NOT_FOUND)
        FavoriteZones.delete()
        #FavoriteZones_payment.save()
        return Response({"message":"FavoriteZones deleted successfully!"},status=status.HTTP_200_OK)


class FavoriteZonesCreateView(generics.CreateAPIView):
    queryset = FavoriteZones.objects.all()
    serializer_class = FavoriteZonesSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({"error":"there is no user with the given user id"},status=status.HTTP_404_NOT_FOUND)
        zone_id = request.data.get('parking_zone')
        try:
            zone = ParkingZone.objects.get(id=zone_id)
        except:
            return Response({"error":"there is no zone with the given zone id"},status=status.HTTP_404_NOT_FOUND)
        
        return super().create(request, *args, **kwargs)



