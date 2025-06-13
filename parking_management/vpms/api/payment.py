from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Payment,Booking,Notification,NotificationUser
from ..serializers import PaymentSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.decorators import api_view,permission_classes
from datetime import timezone,timedelta
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



PAYMENT_PENDING = "pending"
PAYMENT_CANCELLED = "cancelled"
PAYMENT_COMPLETE = "payment complete"
PAYMENT_FAILED = "payment failed"

PAYMENT_METHOD_UNSET = "unset"
PAYMENT_CREATED = "unverified payment created"
PAYMENT_VERIFIED = "payment verified"

# Most methods in this class will only be used for changing payment data irregularly without compliance
# with the payment integration gateway


User = get_user_model()

class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = ["booking__vehicle__plate_number","transaction_id","booking__vehicle_number"]
    filterset_fields = {
    #'name': ['exact', 'icontains'],
    'booking__parking_slot__parking_slot_group__parking_floor__zone__zone_owner__email':['exact'],
    'booking__id':['exact']
    }
    #search_fields = ["parking_slot__slot_number","vehicle__plate_number","vehicle_number"]
    ordering_fields = [field.name for field in Payment._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

class PaymentUserListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in Payment._meta.fields]
    ordering_fields = [field.name for field in Payment._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

    def get_queryset(self):
        id = self.kwargs.get('id')
        queryset = super().get_queryset()
        if id is not None:
            try:
               # Filter the queryset based on the primary key
               queryset = queryset.filter(user_id=User.objects.get(id=id))  # Assuming your model has an 'id' field
               return queryset
            except:
                return Response({"error":"there is no payment with the given id"},status=status.HTTP_400_BAD_REQUEST)
        else:
            # If no 'pk' is provided, return the default queryset (all objects)
            return queryset 
                                                





class PaymentRetrieveView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PaymentUpdateView(generics.UpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PaymentDestroyView(generics.DestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        payment = self.get_object()
        if not payment:
            return Response({"error":"payment not found!"}, status=status.HTTP_404_NOT_FOUND)
        payment.delete()
        #payment.save()
        return Response({"message":"payment deleted successfully!"},status=status.HTTP_200_OK)


class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()

        
        instance = serializer.save()

        notifiction = Notification()
        notifiction.user = self.request.user
        notifiction.notification_type = "payment for booking made"
        notifiction.payment = instance
        notifiction.message = "a new booking payment made by user "+str(self.request.user.email)
        notifiction.is_read = False
        notifiction.created_at = datetime.datetime.now()
        notifiction.save()


    def perform_update(self,serializer):
        validated_data = serializer.validated_data
        validated_data['updated_at'] = datetime.datetime.now()
        serializer.save()



