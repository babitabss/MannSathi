from django import forms
from .models import Transaction, SavingsGoal

class TransactionForm(forms.ModelForm):

    class Meta:
        model  = Transaction
        fields = ['type', 'category', 'amount', 'note', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.TextInput(attrs={'placeholder': 'Optional note'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class SavingsGoalForm(forms.ModelForm):

    class Meta:
        model  = SavingsGoal
        fields = ['name', 'target_amount', 'saved_amount', 'target_date']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Buy a laptop'}),
        }

    def clean(self):
        cleaned_data  = super().clean()
        target_amount = cleaned_data.get('target_amount')
        saved_amount  = cleaned_data.get('saved_amount')

        if target_amount and saved_amount:
            if saved_amount > target_amount:
                raise forms.ValidationError("Saved amount cannot exceed target amount.")

        return cleaned_data