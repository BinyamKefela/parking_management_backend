from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import VehicleType,ParkingZone
from ..serializers import VehicleTypeSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class VehicleTypeListView(generics.ListAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in VehicleType._meta.fields]
    ordering_fields = [field.name for field in VehicleType._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination



class VehicleTypeRetrieveView(generics.RetrieveAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class VehicleTypeUpdateView(generics.UpdateAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class VehicleTypeDestroyView(generics.DestroyAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        VehicleType = self.get_object()
        if not VehicleType:
            return Response({"error":"VehicleType not found!"}, status=status.HTTP_404_NOT_FOUND)
        VehicleType.delete()
        #VehicleType_payment.save()
        return Response({"message":"VehicleType deleted successfully!"},status=status.HTTP_200_OK)


class VehicleTypeCreateView(generics.CreateAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]