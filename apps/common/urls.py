from django.urls import path
from .views import (
    DistrictListView,
    ThanaListView,
    district_thanas,
    locations_summary
)

app_name = 'common'

urlpatterns = [
    # Location endpoints
    path('locations/districts/', DistrictListView.as_view(), name='district-list'),
    path('locations/thanas/', ThanaListView.as_view(), name='thana-list'),
    path('locations/districts/<uuid:district_id>/thanas/', district_thanas, name='district-thanas'),
    path('locations/summary/', locations_summary, name='locations-summary'),
]
