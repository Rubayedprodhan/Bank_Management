from django.contrib import admin
from .models import Transaction
from .views import sent_transaction_mail
# Register your models here.
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account','amount', 'balance_after_transaction' , 'transaction_type', 'loan_approve']
    def save_model(self, request,obj,form, change):
       # if obj.loan_approve ==  True :
        obj.account.balance += obj.amount

        obj.balance_after_transaction = obj.account.balance

        obj.account.save()
        sent_transaction_mail(obj.account.user, obj.amount, 'Admin Loan Approval', 'transactions/admin_email.html')
        super().save_model(request, obj, form, change)

            