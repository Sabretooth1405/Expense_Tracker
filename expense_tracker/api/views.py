from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ExpenseSerializer
from expenses.models import Expense,ExpenseCategory
from django.contrib.auth.models import User
from rest_framework import generics
@api_view(['GET'])
def apiWelcome(req):
    message = {
        'message': " Welcome to the expense tracker api"
    }
    return Response(message)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def apiLoginTest(req):
    message = {
        'message': "You are succesfully logged in"
    }
    return Response(message)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def expenseList(req):
    expenses = Expense.objects.filter(user__username=req.user)
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def expenseDetail(req, pk):
    expenses = Expense.objects.get(user__username=req.user, id=pk)
    serializer = ExpenseSerializer(expenses)
    return Response(serializer.data)

class ExpenseCreateView(generics.CreateAPIView):
    def get_queryset(self):
        return Expense.objects.filter(user__username=self.request.user)
    serializer_class=ExpenseSerializer

    def perform_create(self, serializer):
        id=User.objects.get(username=self.request.user)
        category=ExpenseCategory.objects.get(name=serializer.validated_data.get('category'))
        serializer.save(user=id,category=category)
        return serializer.validated_data


class ExpenseUpdateView(generics.RetrieveUpdateDestroyAPIView):
    
    serializer_class=ExpenseSerializer
    lookup_field='pk'

    def get_queryset(self):
        return Expense.objects.filter(user__username=self.request.user, id=self.kwargs.get('pk'))

    def perform_update(self, serializer):
        id = User.objects.get(username=self.request.user)
        category = ExpenseCategory.objects.get(
            name=serializer.validated_data.get('category'))
        serializer.save(user=id, category=category)
        return serializer.validated_data
