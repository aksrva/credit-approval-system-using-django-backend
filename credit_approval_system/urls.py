from django.urls import path, include
from rest_framework.routers import SimpleRouter
from credit_approval_system.views import (
    CustomerViewset, check_eligibility, create_loan,
    view_loan, view_loans)
router = SimpleRouter()
router.register(r'register', CustomerViewset, basename="cas")

urlpatterns = [
    path('', include(router.urls)),
    path('check-eligibility/', check_eligibility),
    path('create-loan/', create_loan),
    path('view-loan/<int:loan_id>/', view_loan),
    path('view-loans/<int:customer_id>/', view_loans),
]
