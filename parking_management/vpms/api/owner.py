from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Owner
from ..serializers import OwnerSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import Group

OWNER_AVAILABLE = "available"
OWNER_TRIAL = "trial"
OWNER_SUSPENDED = "suspended"
OWNER_CANCELLED = "cancelled"
OWNER_PENDING = "pending"

User = get_user_model()


class OwnerListView(generics.ListAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = ["field.name for field in Owner._meta.fields"]
    ordering_fields = [field.name for field in Owner._meta.fields]
    ordering = ['id']
    lookup_field = 'id'
    pagination_class = CustomPagination





class OwnerRetrieveView(generics.RetrieveAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class OwnerUpdateView(generics.UpdateAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class OwnerDestroyView(generics.DestroyAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        Owner = self.get_object()
        if not Owner:
            return Response({"error":"Owner not found!"}, status=status.HTTP_404_NOT_FOUND)
        Owner.delete()
        #subscription_payment.save()
        return Response({"message":"Owner deleted successfully!"},status=status.HTTP_200_OK)


class OwnerCreateView(generics.CreateAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('company_owner')
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({"error":"there is no user with the given user id"},status=status.HTTP_404_NOT_FOUND)
        #checking whether there is a group with a name Owner in the system
        try:
            user.groups.add(Group.objects.get(name='owner'))
        except:
            return Response({"error":"there is no role owner"},status=status.HTTP_400_BAD_REQUEST)
        #checking whether the user has been assigned a role of a Owner
        if not user.groups.filter(name="owner").exists():
            return Response({"error": "the user you are assigning as an owner does not have a role of an owner, please assign role first."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)



