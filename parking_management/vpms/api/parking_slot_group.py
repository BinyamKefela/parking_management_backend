from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import ParkingSlotGroup,ParkingSlotGroup
from ..serializers import ParkingSlotGroupSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class ParkingSlotGroupListView(generics.ListAPIView):
    queryset = ParkingSlotGroup.objects.all()
    serializer_class = ParkingSlotGroupSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in ParkingSlotGroup._meta.fields]
    ordering_fields = [field.name for field in ParkingSlotGroup._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination





class ParkingSlotGroupRetrieveView(generics.RetrieveAPIView):
    queryset = ParkingSlotGroup.objects.all()
    serializer_class = ParkingSlotGroupSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingSlotGroupUpdateView(generics.UpdateAPIView):
    queryset = ParkingSlotGroup.objects.all()
    serializer_class = ParkingSlotGroupSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingSlotGroupDestroyView(generics.DestroyAPIView):
    queryset = ParkingSlotGroup.objects.all()
    serializer_class = ParkingSlotGroupSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        ParkingSlotGroup = self.get_object()
        if not ParkingSlotGroup:
            return Response({"error":"parking slot group not found!"}, status=status.HTTP_404_NOT_FOUND)
        ParkingSlotGroup.delete()
        #ParkingSlotGroup_payment.save()
        return Response({"message":"parking slot group deleted successfully!"},status=status.HTTP_200_OK)


class ParkingSlotGroupCreateView(generics.CreateAPIView):
    queryset = ParkingSlotGroup.objects.all()
    serializer_class = ParkingSlotGroupSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


