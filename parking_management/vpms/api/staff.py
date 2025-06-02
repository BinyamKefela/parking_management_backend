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
    #filterset_fields = '__all__'
    search_fields = [field.name for field in Staff._meta.fields]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = {
    'owner__email': ['exact'],
    'staff_user__email':['exact']
    }
    ordering_fields = [field.name for field in Staff._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        owner = self.request.user
        try:
            user = owner
            
        except:
            return Response({"error":"there is no user wth the given id"},status=status.HTTP_404_NOT_FOUND)
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        owner = self.request.user
        
        queryset = super().get_queryset()
        queryset.filter(owner=owner)
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

    def update(self, request, *args, **kwargs):
        owner = request.user
        try:
            staff = Staff.objects.get(id=self.kwargs['id'])
            if staff == None:
                return Response({"Error":"staff not found"},status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error":"there is no staff with the given staff id"},status=status.HTTP_404_NOT_FOUND)
        
        user = staff.staff_user
        first_name = request.data.get('first_name',None)
        middle_name = request.data.get('middle_name',None)
        last_name = request.data.get('last_name',None)
        phone_nummber = request.data.get('phone_number',None)
        parking_zone = request.data.get('parking_zone',None)
        if first_name: user.first_name = first_name
        if middle_name: user.middle_name = middle_name
        if last_name: user.last_name = last_name
        if phone_nummber: user.phone_number = phone_nummber
        try:
            if parking_zone: staff.parking_zone = ParkingZone.objects.get(id=parking_zone)
        except:
            return Response({"error":"there is no stparking zone with the given zone id"},status=status.HTTP_404_NOT_FOUND)
        user.save()
        staff.save()
        return Response(StaffSerializer(staff).data,status=status.HTTP_200_OK)


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








@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_staff(request):
    if not request.user.has_perm('vpms.add_staff'):
        return Response({"error":"Unauthorized access"},status=status.HTTP_401_UNAUTHORIZED)
    
    owner = request.user
    #checking whether the user is an owner
    if not owner.groups.filter(name='owner').exists():
        return Response({"error":"There is no owner with the given owner id"},status=status.HTTP_400_BAD_REQUEST)
    email = request.data.get('email')
    first_name = request.data.get('first_name')
    middle_name = request.data.get("middle_name")
    last_name = request.data.get("last_name")
    password = request.data.get("password")
    phone_number = request.data.get("phone_number")
    parking_zone = request.data.get("parking_zone")

    if not all([email, first_name, last_name, password]):
        return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

    staff_user = User()
    staff_user.email = email
    staff_user.first_name = first_name
    staff_user.middle_name = middle_name
    staff_user.last_name = last_name
    staff_user.phone_number = phone_number
    groups = Group.objects.filter(name='staff')
    
    staff_user.set_password(password)
    staff_user.save()

    staff = Staff()
    staff.staff_user = staff_user
    staff.owner = owner
    try:
        staff.parking_zone = ParkingZone.objects.get(id=parking_zone)
    except:
        return Response({"message":"there is no parking zone with the given parking zone id"},status=status.HTTP_400_BAD_REQUEST)
    staff.save()

    staff_user.groups.clear()
    staff_user.groups.set(groups)

    return Response({"message":"successfully created user"},status=status.HTTP_200_OK)      