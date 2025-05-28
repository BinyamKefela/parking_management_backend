from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import PricingRule,ParkingSlot,VehicleType,ParkingZone
from ..serializers import PricingRuleSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class PricingRuleListView(generics.ListAPIView):
    queryset = PricingRule.objects.all()
    serializer_class = PricingRuleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in PricingRule._meta.fields]
    ordering_fields = [field.name for field in PricingRule._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination



class PricingRuleRetrieveView(generics.RetrieveAPIView):
    queryset = PricingRule.objects.all()
    serializer_class = PricingRuleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PricingRuleUpdateView(generics.UpdateAPIView):
    queryset = PricingRule.objects.all()
    serializer_class = PricingRuleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PricingRuleDestroyView(generics.DestroyAPIView):
    queryset = PricingRule.objects.all()
    serializer_class = PricingRuleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        PricingRule = self.get_object()
        if not PricingRule:
            return Response({"error":"PricingRule not found!"}, status=status.HTTP_404_NOT_FOUND)
        PricingRule.delete()
        #PricingRule_payment.save()
        return Response({"message":"PricingRule deleted successfully!"},status=status.HTTP_200_OK)


class PricingRuleCreateView(generics.CreateAPIView):
    queryset = PricingRule.objects.all()
    serializer_class = PricingRuleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


    def create(self, request, *args, **kwargs):
        parking_zone_id = request.data.get('parking_zone')
        vehicle_type_id = request.data.get('vehicle_type')
        try:
            parking_zone = ParkingZone.objects.get(pk=parking_zone_id)
        except:
            return Response({"error":"there is no parking zone with the given zone id"},status=status.HTTP_404_NOT_FOUND)
        try:
            vehicle_type = VehicleType.objects.get(pk=vehicle_type_id)
        except:
            return Response({"error":"there is no vehicle type with the given vehicle type id"},status=status.HTTP_404_NOT_FOUND)
        return super().create(request, *args, **kwargs)
