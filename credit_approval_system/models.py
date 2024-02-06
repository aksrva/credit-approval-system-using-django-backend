from django.db import models


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10, unique=True)
    age = models.IntegerField(null=True, blank=True)
    monthly_income = models.IntegerField(default=0, null=True, blank=True)
    approved_limit = models.IntegerField(default=0, null=True, blank=True)
    current_debt = models.IntegerField(default=0, null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now_add=False, auto_now=True,
                                   null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Loan(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_id = models.IntegerField(null=True, blank=True)
    loan_amount = models.IntegerField(default=0)
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    paid_on_time = models.BooleanField(default=False)
    monthly_payment = models.IntegerField()
    emi_paid_on_time = models.IntegerField(default=0)
    date_of_approval = models.DateField()
    end_date = models.DateField()
    created_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now_add=False, auto_now=True,
                                   null=True)

    def __str__(self):
        return f"{self.customer_id} -- {self.loan_id}"
