from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Transaction, SavingsGoal
from .forms import TransactionForm, SavingsGoalForm

@login_required
def finance_dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)

    # Calculate totals using ORM aggregation
    total_income  = transactions.filter(type='income').aggregate(
                        total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(type='expense').aggregate(
                        total=Sum('amount'))['total'] or 0
    balance       = total_income - total_expense

    # Recent 10 transactions
    recent       = transactions[:10]
    goals        = SavingsGoal.objects.filter(user=request.user, status='active')

    return render(request, 'finance/dashboard.html', {
        'total_income':  total_income,
        'total_expense': total_expense,
        'balance':       balance,
        'recent':        recent,
        'goals':         goals,
    })


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction      = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, "Transaction added successfully.")
            return redirect('finance_dashboard')
    else:
        form = TransactionForm()

    return render(request, 'finance/add_transaction.html', {'form': form})


@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction deleted.")
    return redirect('finance_dashboard')


@login_required
def add_goal(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal      = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Savings goal created.")
            return redirect('finance_dashboard')
    else:
        form = SavingsGoalForm()

    return render(request, 'finance/add_goal.html', {'form': form})


@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, "Goal deleted.")
    return redirect('finance_dashboard')