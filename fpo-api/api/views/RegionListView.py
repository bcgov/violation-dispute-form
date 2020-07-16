from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import generics
from api.models import Region
from api.serializers import RegionLookupSerializer
from api.auth import IsActiveAndAdminUser


class RegionListView(generics.ListAPIView):
    queryset = ""
    permission_classes = [IsActiveAndAdminUser]

    def get(self, request: Request, *args, **kwargs):
        queryset = Region.objects.all()
        serializer = RegionLookupSerializer(queryset, many=True)
        return Response(serializer.data)
