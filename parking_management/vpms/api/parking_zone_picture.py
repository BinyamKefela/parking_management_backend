from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import ParkingZonePicture,ParkingZonePicture
from ..serializers import ParkingZonePictureSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class ParkingZonePictureListView(generics.ListAPIView):
    queryset = ParkingZonePicture.objects.all()
    serializer_class = ParkingZonePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in ParkingZonePicture._meta.fields]
    ordering_fields = [field.name for field in ParkingZonePicture._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination





class ParkingZonePictureRetrieveView(generics.RetrieveAPIView):
    queryset = ParkingZonePicture.objects.all()
    serializer_class = ParkingZonePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingZonePictureUpdateView(generics.UpdateAPIView):
    queryset = ParkingZonePicture.objects.all()
    serializer_class = ParkingZonePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ParkingZonePictureDestroyView(generics.DestroyAPIView):
    queryset = ParkingZonePicture.objects.all()
    serializer_class = ParkingZonePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        ParkingZonePicture = self.get_object()
        if not ParkingZonePicture:
            return Response({"error":"parking zone picture not found!"}, status=status.HTTP_404_NOT_FOUND)
        ParkingZonePicture.delete()
        #ParkingZonePicture_payment.save()
        return Response({"message":"parking zone picture deleted successfully!"},status=status.HTTP_200_OK)


class ParkingZonePictureCreateView(generics.CreateAPIView):
    queryset = ParkingZonePicture.objects.all()
    serializer_class = ParkingZonePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


