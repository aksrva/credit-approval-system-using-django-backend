from rest_framework import serializers
from credit_approval_system.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(
        'get_name', read_only=True)
    customer_id = serializers.SerializerMethodField(
        'get_customer_id', read_only=True)

    class Meta:
        model = Customer
        fields = ("customer_id", "name", "age", "monthly_salary",
                  "approved_limit", "phone_number")

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_customer_id(self, obj):
        return obj.pk


class CustomerPostSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(
        'get_name', read_only=True)

    class Meta:
        model = Customer
        fields = ("name", "id", "first_name", "last_name", "age",
                  "approved_limit", "monthly_salary", "phone_number")

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class LoanCheckEligibility(serializers.ModelSerializer):
    class Meta:
        pass
