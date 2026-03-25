from django.urls import path

from fees.views import (
    FeePaymentListCreateView,
    FeePaymentRetrieveUpdateDestroyView,
    FeeStructureListCreateView,
    FeeStructureRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("structures/", FeeStructureListCreateView.as_view(), name="fee-structures"),
    path(
        "structures/<int:pk>/",
        FeeStructureRetrieveUpdateDestroyView.as_view(),
        name="fee-structure-detail",
    ),
    path("payments/", FeePaymentListCreateView.as_view(), name="fee-payments"),
    path(
        "payments/<int:pk>/",
        FeePaymentRetrieveUpdateDestroyView.as_view(),
        name="fee-payment-detail",
    ),
]

