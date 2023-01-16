from rest_framework import serializers
from expenses.models import Expense, ExpenseCategory
from django.contrib.auth.models import User
from rest_framework.response import Response


class CategoryRelatedField(serializers.RelatedField):
    def display_value(self, instance):
        return instance

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        return ExpenseCategory.objects.get(name=data)

class ExpenseSerializer(serializers.ModelSerializer):
    category = CategoryRelatedField(
        queryset=ExpenseCategory.objects.all()
    )

    class Meta:
        model = Expense
        fields = ['user','amount','category','description','date','created_at']
        extra_kwargs = {'user': {'required': False}}
        read_only_fields=('user',)

    def to_representation(self, data):
        data = super(ExpenseSerializer, self).to_representation(data)
        username = User.objects.filter(pk=data['user']).first().username
        data['user'] = username
        return data

    
