from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Staff,ParkingZone
from ..serializers import StaffSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import permission_classes,api_view
from django.contrib.auth.models import Group



User = get_user_model()


#this API was made in a way such that it returns the staff of a specific owner
class StaffListView(generics.ListAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in Staff._meta.fields]
    ordering_fields = [field.name for field in Staff._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

    def get_queryset(self):
        owner_id = self.kwargs.get('owner_id')
        try:
            user = User.objects.get(pk=owner_id)
            if not user.groups.filter(name='owner').exists():
                return Response({"error":"there is no owner with the given id"},status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error":"there is no user wth the given id"},status=status.HTTP_404_NOT_FOUND)
        queryset = super().get_queryset()
        queryset.filter(owner=owner_id)
        return queryset





class StaffRetrieveView(generics.RetrieveAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class StaffUpdateView(generics.UpdateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class StaffDestroyView(generics.DestroyAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        Staff = self.get_object()
        if not Staff:
            return Response({"error":"Staff not found!"}, status=status.HTTP_404_NOT_FOUND)
        Staff.delete()
        #Staff_payment.save()
        return Response({"message":"Staff deleted successfully!"},status=status.HTTP_200_OK)








@api_view(['GET'])
@permission_classes([IsAuthenticated])
def create_staff(request,owner_id,email,first_name,middle_name,last_name,password):
    try:
        owner = User.objects.get(pk=owner_id)
    except:
        return Response({"error":"There is no user with the given owner id"},status=status.HTTP_400_BAD_REQUEST)
    if not owner.groups.filter(name='owner').exists():
        return Response({"error":"There is no owner with the given owner id"},status=status.HTTP_400_BAD_REQUEST)
    
    staff_user = User()
    staff_user.email = email
    staff_user.first_name = first_name
    staff_user.middle_name = middle_name
    staff_user.last_name = last_name
    groups = Group.objects.filter(name='staff')
    staff_user.groups.clear()
    staff_user.groups.set(groups)
    staff_user.set_password(password)
    staff_user.save()

    staff = Staff()
    staff.staff_user = staff_user
    staff.owner = owner
    staff.save()

    return Response({"message":"successfully created user"},status=status.HTTP_200_OK)


      