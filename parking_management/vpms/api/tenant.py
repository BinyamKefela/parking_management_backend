from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Tenant,Rent
from ..serializers import TenantSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

TENANT_AVAILABLE = "available"
TENANT_TRIAL = "trial"
TENANT_SUSPENDED = "suspended"
TENANT_CANCELLED = "cancelled"
TENANT_PENDING = "pending"

User = get_user_model()


class TenantListView(generics.ListAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in Tenant._meta.fields]
    ordering_fields = [field.name for field in Tenant._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination





class TenantRetrieveView(generics.RetrieveAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class TenantUpdateView(generics.UpdateAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class TenantDestroyView(generics.DestroyAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        Tenant = self.get_object()
        if not Tenant:
            return Response({"error":"Tenant not found!"}, status=status.HTTP_404_NOT_FOUND)
        Tenant.delete()
        #subscription_payment.save()
        return Response({"message":"Tenant deleted successfully!"},status=status.HTTP_200_OK)


class TenantCreateView(generics.CreateAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('company_owner_id')
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({"error":"there is no user with the given user id"},status=status.HTTP_404_NOT_FOUND)
        if user.groups.filter(name="tenant").exists:
            return Response({"error": "the user you are assigning as a tenant does not have a role of a tenant, please assign role first."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)



