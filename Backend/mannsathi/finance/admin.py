from django.contrib import admin
from .models import Transaction, SavingsGoal

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'type', 'category', 'amount', 'date']
    list_filter   = ['type', 'category']
    search_fields = ['user__username', 'note']

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display  = ['user', 'name', 'target_amount', 'saved_amount', 'target_date', 'status']
    list_filter   = ['status']
    search_fields = ['user__username', 'name']