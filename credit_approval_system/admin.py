from django.contrib import admin
from credit_approval_system.models import Customer, Loan
from import_export.admin import ImportExportModelAdmin


class CustomerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone_number",
                    "age", "monthly_income", "approved_limit",
                    "current_debt", "created_date", "update_date")


class LoanAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ("customer_id", "loan_id", "loan_amount", "tenure",
                    "interest_rate", "paid_on_time", "monthly_payment",
                    "emi_paid_on_time", "date_of_approval", "end_date")
    list_filter = ['paid_on_time']


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Loan, LoanAdmin)
