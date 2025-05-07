from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import ParkingSlot,ParkingZone
from ..serializers import ParkingSlotSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class ParkingSlotListView(generics.ListAPIView):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in ParkingSlot._meta.fields]
    ordering_fields = [field.name for field in ParkingSlot._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination





class ParkingSlotRetrieveView(generics.RetrieveAPIView):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingSlotUpdateView(generics.UpdateAPIView):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingSlotDestroyView(generics.DestroyAPIView):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        ParkingSlot = self.get_object()
        if not ParkingSlot:
            return Response({"error":"ParkingSlot not found!"}, status=status.HTTP_404_NOT_FOUND)
        ParkingSlot.delete()
        #ParkingSlot_payment.save()
        return Response({"message":"ParkingSlot deleted successfully!"},status=status.HTTP_200_OK)


class ParkingSlotCreateView(generics.CreateAPIView):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def create(self, request, *args, **kwargs):
        user_id = ParkingSlot.objects.get(request.data.get('zone_id')).zone.zone_owner.pk
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({"error":"there is no owner associated with the given zone id"},status=status.HTTP_404_NOT_FOUND)
        if user.groups.filter(name="owner").exists():
            return Response({"error": "the user you are trying to create a ParkingSlot for does not have a role of an owner, please assign role first."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)



