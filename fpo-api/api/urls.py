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

from django.urls import include, path
from django.conf import settings

# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework.schemas import SchemaGenerator
# from rest_framework.views import APIView
# from rest_framework_swagger import renderers

# from rest_framework.urlpatterns import format_suffix_patterns

import api.views as views
from .views_old import SubmitTicketResponseView

# class SwaggerSchemaView(APIView):
#     permission_classes = [AllowAny]
#     renderer_classes = [renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer]
#     _ignore_model_permissions = True
#     exclude_from_schema = True

#     def get(self, request):
#         generator = SchemaGenerator()
#         schema = generator.get_schema(request=request)
#         return Response(schema)


urlpatterns = [
    # Swagger documentation
    # url(r'^$', SwaggerSchemaView.as_view()), 
    path("submit-form/", SubmitTicketResponseView.as_view()),
    path("responses/counts/", views.TicketCountView.as_view()),
    path("responses/", views.TicketResponseListView.as_view()),
    path("locations/", views.LocationListView.as_view()),
    path("regions/", views.RegionListView.as_view()),
    path("pdf/<int:id>/", views.PdfFileView.as_view()),
    path("pdf/", views.LocationListView.as_view()),
    path("archived/", views.ArchivedView.as_view())
]

if settings.OIDC_ENABLED:
    urlpatterns.append(path("oidc/", include("oidc_rp.urls")))

# urlpatterns = format_suffix_patterns(urlpatterns)
