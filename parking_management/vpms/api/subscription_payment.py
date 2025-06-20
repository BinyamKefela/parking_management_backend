from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import SubscriptionPayment
from ..serializers import SubscriptionPaymentSerializer
from vpms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import status



SUBSCRIPTION_PAYMENT_PENDING = "pending"
SUBSCRIPTION_PAYMENT_COMPLETE = "complete"
SUBSCRIPTION_PAYMENT_CANCELLED = "cancelled"


class SubscriptionPaymentListView(generics.ListAPIView):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in SubscriptionPayment._meta.fields]
    ordering_fields = [field.name for field in SubscriptionPayment._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination


class SubscriptionPaymentRetrieveView(generics.RetrieveAPIView):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SubscriptionPaymentUpdateView(generics.UpdateAPIView):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SubscriptionPaymentDestroyView(generics.DestroyAPIView):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        subscription_payment = self.get_object()
        if not subscription_payment:
            return Response({"error":"subscription payment not found!"}, status=status.HTTP_404_NOT_FOUND)
        subscription_payment.status = SUBSCRIPTION_PAYMENT_CANCELLED
        subscription_payment.save()
        return Response({"message":"subscription payment deleted successfully!"},status=status.HTTP_200_OK)



class SubscriptionPaymentCreateView(generics.CreateAPIView):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    