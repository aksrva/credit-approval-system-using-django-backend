import random
from django.http import HttpResponse
from credit_approval_system.models import Customer, Loan
from credit_approval_system.serializers import (CustomerSerializer,
                                                CustomerPostSerializer)
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from datetime import datetime, timedelta
import math


def home(request):
    return HttpResponse("Credit Approval System")


class CustomerViewset(mixins.ListModelMixin,
                      mixins.CreateModelMixin, viewsets.GenericViewSet):
    default_serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    serializer_classes = {
        "list": CustomerSerializer,
        "create": CustomerPostSerializer}

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action,
                                           self.default_serializer_class)

    def create(self, request, *args, **kwargs):
        approved_limit = round(36 * request.data.get('monthly_income'), -5)
        request.data['approved_limit'] = approved_limit
        resp = super().create(request, *args, **kwargs)
        object = self.queryset.filter(pk=resp.data.get('id')).first()
        serializer = CustomerSerializer(object, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False,
            methods=['get'],
            url_path='(?P<customer_id>[^/.]+)')
    def get_customer(self, request, customer_id, *args, **kwargs):
        instance = self.queryset.filter(pk=customer_id).first()
        serializer = CustomerSerializer(instance, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


def approval(customer_id, loan_amount, interest_rate, tenure):
    queryset = Loan.objects.filter(customer_id__id=customer_id)
    customer = Customer.objects.filter(pk=customer_id).first()
    current_date = datetime.now().date()
    no_of_active_loan = 0
    no_of_loan = queryset.count()

    # Calculated credit rating
    credit_rating = 0
    current_loan_amount = 0
    current_emi = 0
    for loan in queryset:
        if loan.end_date > current_date:
            current_loan_amount += loan.loan_amount
            no_of_active_loan += 1
        if loan.paid_on_time:
            credit_rating += 20
        if current_loan_amount > customer.approved_limit:
            credit_rating += 10
        current_emi += loan.monthly_payment
    credit_rating += no_of_active_loan * 10
    credit_rating += no_of_loan*5
    # Approval
    approval = False
    corrected_interest_rate = 0
    monthly_installment = 0

    if credit_rating > 50:
        approval = True
    elif 50 > credit_rating > 30:
        approval = True
        corrected_interest_rate = max(float(interest_rate), 12.0)
    elif 30 > credit_rating > 10:
        approval = True
        corrected_interest_rate = max(float(interest_rate), 16.0)
    else:
        corrected_interest_rate = float(interest_rate)

    if current_emi < customer.monthly_income * 0.5:
        approval = True
    else:
        approval = False

    # EMI calculate
    if approval:
        monthly_interest_rate = corrected_interest_rate / (12 * 100)
        duration = tenure
        emi = (
            loan_amount * monthly_interest_rate * math.pow(
                1 + monthly_interest_rate, duration)) / (
                    math.pow(1 + monthly_interest_rate, duration) - 1)
        monthly_installment = round(emi, 2)

    return (approval, tenure,
            corrected_interest_rate, monthly_installment)


@api_view(["POST"])
def check_eligibility(request):
    customer_id = request.data.get('customer_id')
    loan_amount = request.data.get('loan_amount')
    interest_rate = request.data.get('interest_rate')
    tenure = request.data.get('tenure')
    is_approval, tenure, corrected_interest_rate, monthly_installment =\
        approval(customer_id, loan_amount, interest_rate, tenure)

    response = {
        'customer_id': customer_id,
        'approval': is_approval,
        'interest_rate': corrected_interest_rate,
        'tenure': tenure,
        'monthly_installment': monthly_installment
    }

    return Response(response)


@api_view(["POST"])
def create_loan(request):
    customer_id = request.data.get('customer_id')
    loan_amount = request.data.get('loan_amount')
    interest_rate = request.data.get('interest_rate')
    tenure = request.data.get('tenure')
    is_approval, tenure, corrected_interest_rate, monthly_installment =\
        approval(customer_id, loan_amount, interest_rate, tenure)
    customer = Customer.objects.filter(pk=customer_id).first()
    if not is_approval:
        response = {
            "customer_id": customer,
            "loan_approved": is_approval,
            "message": ("Oops! Due to Internal reason your loan approval"
                        "rejected.")
        }
        return Response(response)
    r_loan_id = random.randint(1000, 9999)
    date_of_approval = datetime.now().date()
    Loan.objects.create(
        customer_id=customer,
        loan_id=r_loan_id,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=corrected_interest_rate,
        monthly_payment=monthly_installment,
        date_of_approval=date_of_approval,
        end_date=date_of_approval + timedelta(days=365 * tenure))
    response = {
        "loan_id": r_loan_id,
        "customer_id": customer_id,
        "loan_approved": is_approval,
        "message": "Congratulation!!, Your Loan has been approved.",
        "monthly_installment": monthly_installment
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(["GET"])
def view_loan(request, loan_id):
    loan_response = Loan.objects.filter(loan_id=loan_id).last()
    if not loan_response:
        return Response({"message": "Not found!!"},
                        status=status.HTTP_404_NOT_FOUND)
    response = {}
    response['loan_id'] = loan_response.loan_id
    customer = Customer.objects.filter(pk=loan_response.customer_id.pk).last()
    response['customer'] = {
        "id": customer.pk,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "phone_number": customer.phone_number,
        "age": customer.age}
    response['loan_amount'] = loan_response.loan_amount
    response['interest_rate'] = loan_response.interest_rate
    response['monthly_installment'] = loan_response.monthly_payment

    return Response(response, status=status.HTTP_200_OK)


@api_view(["GET"])
def view_loans(request, customer_id):
    loan_response = Loan.objects.filter(customer_id__id=customer_id).last()
    if not loan_response:
        return Response({"message": "Not found!!"},
                        status=status.HTTP_404_NOT_FOUND)
    response = {
        "loan_id": loan_response.loan_id,
        "loan_amount": loan_response.loan_amount,
        "monthly_installment": loan_response.monthly_payment,
        "repayments_left": (
            loan_response.tenure - loan_response.emi_paid_on_time)
    }

    return Response(response, status=status.HTTP_200_OK)
