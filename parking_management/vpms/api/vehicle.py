from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Vehicle,ParkingZone
from ..serializers import VehicleSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class VehicleListView(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in Vehicle._meta.fields]
    ordering_fields = [field.name for field in Vehicle._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination



class VehicleRetrieveView(generics.RetrieveAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class VehicleUpdateView(generics.UpdateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class VehicleDestroyView(generics.DestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        Vehicle = self.get_object()
        if not Vehicle:
            return Response({"error":"Vehicle not found!"}, status=status.HTTP_404_NOT_FOUND)
        Vehicle.delete()
        #Vehicle_payment.save()
        return Response({"message":"Vehicle deleted successfully!"},status=status.HTTP_200_OK)


class VehicleCreateView(generics.CreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({"error":"there is no user with the given user id"},status=status.HTTP_404_NOT_FOUND)
        return super().create(request, *args, **kwargs)