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
from rest_framework.decorators import api_view,permission_classes

OWNER_ACTIVE = "active"
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
    filterset_fields = {
    'company_name': ['exact', 'icontains'],
    'company_email': ['exact', 'icontains'],
    'company_phone_number': ['exact', 'icontains'],
    'company_address': ['exact', 'icontains'],
    'status': ['exact'],
    'company_owner__email': ['exact', 'icontains'],
    'company_owner__first_name': ['icontains'],
    'company_owner__last_name': ['icontains'],
    'plan': ['exact'],
    'created_at': ['date', 'date__gte', 'date__lte'],}
    
    search_fields = ["company_owner__email","company_name","company_email","company_phone_number","company_address"]
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

    '''def update(self, request, *args, **kwargs):
        user = request.user
        company_owner_id = request.data.get("company_owner")
        try:
            company_owner = User.data.get(id=company_owner_id)
        except:
            return Response({"error":"there is no user with the given owner id"},status=status.HTTP_400_BAD_REQUEST)
        if (not company_owner.pk==user.pk) and (not user.is_superuser):
            return Response({"error":"the given owner has not logged in"},status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)'''


class OwnerDestroyView(generics.DestroyAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        owner = self.get_object()
        if not owner:
            return Response({"error":"Owner not found!"}, status=status.HTTP_404_NOT_FOUND)
        owner.status="cancelled"
        try:
            user = owner.company_owner
            #user.groups.remove(Group.objects.filter(name="owner"))
            user.is_active = False
            user.save()
        except:
            return Response({"error":"There is no user with the given owner id"},status=status.HTTP_400_BAD_REQUEST)
        owner.save()
        #subscription_payment.save()
        return Response({"message":"Owner deactivated successfully!"},status=status.HTTP_200_OK)


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
        if Owner.objects.filter(company_owner=user).count() > 0:
            return Response({"error":"the user is already an owner,check if the owner status"},status=status.HTTP_400_BAD_REQUEST)
        #checking whether there is a group with a name Owner in the system
        try:
            user.groups.clear()
            user.groups.add(Group.objects.get(name='owner'))
        except:
            return Response({"error":"there is no role owner"},status=status.HTTP_400_BAD_REQUEST)
        #checking whether the user has been assigned a role of a Owner
        if not user.groups.filter(name="owner").exists():
            return Response({"error": "the user you are assigning as an owner does not have a role of an owner, please assign role first."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def activate_owner(request):
    owner_id = request.data.get('owner')
    try:
        owner = Owner.objects.get(pk=owner_id)
        user = owner.company_owner
        if not user:
            return Response({"error":"there is no active user with the given user id"},status=status.HTTP_404_NOT_FOUND)
        user.is_active=True
        user.save()
    except:
        return Response({"error":"there is no user associated with the given owner id"},status=status.HTTP_404_NOT_FOUND)
    owner.status = OWNER_ACTIVE
    return Response({"message":"owner activated successfully"},status=status.HTTP_200_OK)
    
    


