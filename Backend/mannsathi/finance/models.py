from django.db import models
from django.conf import settings

class Transaction(models.Model):

    TYPE_CHOICES = [
        ('income',  'Income'),
        ('expense', 'Expense'),
    ]

    CATEGORY_CHOICES = [
        ('food',          'Food'),
        ('rent',          'Rent'),
        ('transport',     'Transport'),
        ('health',        'Health'),
        ('education',     'Education'),
        ('entertainment', 'Entertainment'),
        ('savings',       'Savings'),
        ('remittance',    'Remittance'),
        ('salary',        'Salary'),
        ('freelance',     'Freelance'),
        ('other',         'Other'),
    ]

    user     = models.ForeignKey(
                   settings.AUTH_USER_MODEL,
                   on_delete=models.CASCADE,
                   related_name='transactions'
               )
    type     = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount   = models.DecimalField(max_digits=10, decimal_places=2)
    note     = models.CharField(max_length=255, blank=True, null=True)
    date     = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.type} — NPR {self.amount}"


class SavingsGoal(models.Model):

    STATUS_CHOICES = [
        ('active',    'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user          = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        related_name='savings_goals'
                    )
    name          = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    saved_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date   = models.DateField()
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.name}"

    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        percentage = (self.saved_amount / self.target_amount) * 100
        return min(round(percentage, 1), 100)

    def remaining(self):
        return max(self.target_amount - self.saved_amount, 0)