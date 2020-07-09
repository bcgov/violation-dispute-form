"""
    REST API Documentation for Family Protection Order

    OpenAPI spec version: v1


    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from rest_framework import serializers

from api.models import TicketResponse, Location, Region, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = Location
        fields = "__all__"


class TicketResponseSerializer(serializers.ModelSerializer):
    hearing_location = LocationSerializer()
    printed_by = UserSerializer()
    archived_by = UserSerializer()

    class Meta:
        model = TicketResponse
        # if the size of the response is becoming a problem
        # exclude = ["result"]
        fields = "__all__"


class LocationLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name"]


class RegionLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "name"]
