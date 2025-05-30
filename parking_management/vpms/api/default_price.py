from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import DefaultPrice
from ..serializers import DefaultPriceSerializer
from vpms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model


User = get_user_model()

#an API for getting all the DefaultPrices of all users
class DefaultPriceListView(generics.ListAPIView):
    queryset = DefaultPrice.objects.all()
    serializer_class = DefaultPriceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    #filter_backends = [SearchFilter, OrderingFilter]
    #search_fields = [field.name for field in DefaultPrice._meta.fields]
    filterset_fields = {
    'parking_zone__zone_owner__email': ['exact',],
    }
    search_fields = ["parking_zone__name","rate"]
    ordering_fields = [field.name for field in DefaultPrice._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination





# an API for getting a specific DefaultPrice
class DefaultPriceRetrieveView(generics.RetrieveAPIView):
    queryset = DefaultPrice.objects.all()
    serializer_class = DefaultPriceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class DefaultPriceUpdateView(generics.UpdateAPIView):
    queryset = DefaultPrice.objects.all()
    serializer_class = DefaultPriceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class DefaultPriceDestroyView(generics.DestroyAPIView):
    queryset = DefaultPrice.objects.all()
    serializer_class = DefaultPriceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        DefaultPrice = self.get_object()
        if not DefaultPrice:
            return Response({"error":"DefaultPrice not found!"}, status=status.HTTP_404_NOT_FOUND)
        DefaultPrice.delete()
        #DefaultPrice.save()
        return Response({"message":"DefaultPrice deleted successfully!"},status=status.HTTP_200_OK)



class DefaultPriceCreateView(generics.CreateAPIView):
    queryset = DefaultPrice.objects.all()
    serializer_class = DefaultPriceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    