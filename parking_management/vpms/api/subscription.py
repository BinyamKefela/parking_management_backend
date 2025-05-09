from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Subscription
from ..serializers import SubscriptionSerializer
from vpms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from vpms.models import Owner


User = get_user_model()


class SubscriptionListView(generics.ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = '__all__'
    search_fields = [field.name for field in Subscription._meta.fields]
    ordering_fields = [field.name for field in Subscription._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination





class SubscriptionRetrieveView(generics.RetrieveAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SubscriptionUpdateView(generics.UpdateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SubscriptionDestroyView(generics.DestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        Subscription = self.get_object()
        if not Subscription:
            return Response({"error":"Subscription not found!"}, status=status.HTTP_404_NOT_FOUND)
        Subscription.delete()
        #subscription_payment.save()
        return Response({"message":"Subscription deleted successfully!"},status=status.HTTP_200_OK)


class SubscriptionCreateView(generics.CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def create(self, request, *args, **kwargs):
        owner_id = request.data.get('owner')
        try:
            owner = Owner.objects.get(id=owner_id)
        except:
            return Response({"error":"there is no owner with the given owner id"},status=status.HTTP_404_NOT_FOUND)
        
        return super().create(request, *args, **kwargs)



