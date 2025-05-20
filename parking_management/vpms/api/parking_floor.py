from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import ParkingFloor,ParkingZone
from ..serializers import ParkingFloorSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class ParkingFloorListView(generics.ListAPIView):
    queryset = ParkingFloor.objects.all()
    serializer_class = ParkingFloorSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in ParkingFloor._meta.fields]
    ordering_fields = [field.name for field in ParkingFloor._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination





class ParkingFloorRetrieveView(generics.RetrieveAPIView):
    queryset = ParkingFloor.objects.all()
    serializer_class = ParkingFloorSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingFloorUpdateView(generics.UpdateAPIView):
    queryset = ParkingFloor.objects.all()
    serializer_class = ParkingFloorSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingFloorDestroyView(generics.DestroyAPIView):
    queryset = ParkingFloor.objects.all()
    serializer_class = ParkingFloorSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        ParkingFloor = self.get_object()
        if not ParkingFloor:
            return Response({"error":"ParkingFloor not found!"}, status=status.HTTP_404_NOT_FOUND)
        ParkingFloor.delete()
        #ParkingFloor_payment.save()
        return Response({"message":"ParkingFloor deleted successfully!"},status=status.HTTP_200_OK)


class ParkingFloorCreateView(generics.CreateAPIView):
    queryset = ParkingFloor.objects.all()
    serializer_class = ParkingFloorSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def create(self, request, *args, **kwargs):
        try:
           user_id = ParkingZone.objects.get(id=request.data.get('zone')).zone_owner.pk
        except:
           return Response({"error":"there is no parking zone associated with the given zone id"},status=status.HTTP_404_NOT_FOUND) 
        #checking whether there is a user associated with the parking floor's parking zone
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({"error":"there is no owner associated with the given zone id"},status=status.HTTP_404_NOT_FOUND)
        #checking whether there is an owner associated with the parking floor's parking zone
        if user.groups.filter(name="owner").exists():
            return Response({"error": "the user you are trying to create a ParkingFloor for does not have a role of an owner, please assign role first."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)



