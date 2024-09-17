from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositForm, WithdrawForm, LoanRequestForm
from .constants import DEPOSIT, WITHDRAWAL, LOAN, LOAN_PAID
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic.list import ListView
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import TransferForm
from accounts.models import UserBankAccount
from .constants import TRANSACTION_TYPE_TRANSFER_IN, TRANSACTION_TYPE_TRANSFER_OUT
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
# Create your views here.

def sent_transaction_mail(user, amount, subject, template):
        message = render_to_string(template,{
            'user' : user,
            'amount' : amount
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()

   
class TransactionCreateMinxin(LoginRequiredMixin, CreateView):
  
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                'account' : self.request.user.account
            }
        )
        return kwargs
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'title' : self.title
            }
        )
        return context
class DepositMoneyViews(TransactionCreateMinxin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type' : DEPOSIT}
        return initial 
    

    def form_valid(self,form):
       # if form.is_valid():
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance +=  amount
        account.save(
            update_fields = ['balance']
        )

        messages.success(self.request, f"{amount}$ was Deposited to You account successfully")
        sent_transaction_mail(self.request.user, amount, 'Deposited Massages','transactions/deposit_email.html')
        return super().form_valid(form)
    

class WithdrawMoneyViews(TransactionCreateMinxin, FormView):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': 'WITHDRAWAL'} 
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        user_account = self.request.user.account

     
        if amount is None or amount <= 0:
            messages.error(self.request, ' Withdrawal amount must be greater than zero.')
            return self.form_invalid(form)

     
        total_bank_balance = UserBankAccount.objects.aggregate(total_balance=Sum('balance'))['total_balance'] or 0

    
        if total_bank_balance < amount:
            messages.error(self.request, 'The bank is currently bankrupt and cannot process your withdrawal.')
            return self.form_invalid(form)

      
        if amount > user_account.balance:
            messages.error(self.request, 'Insufficient funds in your account.')
            return self.form_invalid(form)

     
        user_account.balance -= amount
        user_account.save(update_fields=['balance'])

       
        self.transaction(
            account=user_account,
            amount=-amount,
            balance_after_transaction=user_account.balance,
            transaction_type='WITHDRAWAL'  
        )

        messages.success(self.request, f"{amount}$ was withdrawn from your account successfully.")
        sent_transaction_mail(self.request.user, amount, 'Withdrawal Confirmation', 'transactions/Withdrawal_email.html')

        return super().form_valid(form)

    def form_invalid(self, form):
        
        return super().form_invalid(form)

# class WithdrawMoneyViews(TransactionCreateMinxin):
#     form_class = WithdrawForm
#     title = 'Withdraw Money'

#     def get_initial(self):
#         initial = {'transaction_type' : WITHDRAWAL}
#         return initial 
    

#     def form_valid(self,form):
#        # if form.is_valid():
#         amount = form.cleaned_data.get('amount')
#         account = self.request.user.account
#         account.balance -=  amount
#         account.save(
#             update_fields = ['balance']
#         )

#         messages.success(self.request, f"{amount}$ was Withdrawal to You account successfully")
#         sent_transaction_mail(self.request.user, amount, 'Withdrawal Massages','transactions/Withdrawal_email.html')
#         return super().form_valid(form)


class LoanRequestViews(TransactionCreateMinxin):
    form_class = LoanRequestForm
    title = 'Request For Loan'
    

    def get_initial(self):
        initial = {'transaction_type' : LOAN}
        return initial 
    def form_valid(self,form):
       # if form.is_valid():
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(account = self.request.user.account, transaction_type=3, loan_approve = True).count()
        if current_loan_count >= 3:
            return HttpResponse("You have crossed your limits")
        

        messages.success(self.request, f"Loan Request for amount {amount}$ has been successfully sent to admin")
        sent_transaction_mail(self.request.user, amount, 'Loan Request Massages','transactions/loan_email.html')
        return super().form_valid(form)
 
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0
    context_object_name = "repot_list"

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account = self.request.user.account
        )
        
        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")
        if start_date_str and end_date_str:

            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date
            
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date
            #queryset = queryset.filter(timestamp__date__gte=start_date,timestamp__date__lte=end_date)
            
            #queryset = queryset.filter(timestamp__date__get = start_date,timestamp__date__lte = end_date)
            self.balance = Transaction.objects.filter(timestamp__date__gte= start_date,
                timestamp__date__lte = end_date).aggregate(Sum('amount'))['amount_sum']
            
        else:
            self.balance = self.request.user.account.balance

        return queryset
        
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'account' : self.request.user.account
            }
        )
        return context
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan= get_object_or_404(Transaction, id=loan_id)
        if loan.loan_approve:
            user_account = loan.account
            if loan.amount <= user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transction = user_account.balance
                user_account.save()
                loan.transaction_type =LOAN_PAID
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(self.request, f"Loan amount  is gerter then available balance")
                
                return redirect('loan_list')

class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
  
    template_name = 'transactions/loan_request.html'
    context_object_name = "loans"
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account, transaction_type=LOAN)
        return queryset
        
        
class TransferMoneyView(FormView):
    template_name = 'transactions/money_sent_received.html'
    form_class = TransferForm
    success_url = reverse_lazy('transfer_money')

    def form_valid(self, form):
        account_number = form.cleaned_data.get('account_number')
        amount = form.cleaned_data.get('amount')

       
        try:
            recipient_account = UserBankAccount.objects.get(account_no=account_number)
        except UserBankAccount.DoesNotExist:
            messages.error(self.request, 'Recipient account not found.')
            return self.form_invalid(form)

        
        sender_account = self.request.user.account

        if amount > sender_account.balance:
            messages.error(self.request, 'Insufficient funds.')
            return self.form_invalid(form)

     
        sender_account.balance -= amount
        recipient_account.balance += amount
        sender_account.save()
        recipient_account.save()

        
        Transaction.objects.create(
            account=sender_account,
            amount=-amount,
            balance_after_transaction=sender_account.balance,
            transaction_type=TRANSACTION_TYPE_TRANSFER_OUT
        )

        Transaction.objects.create(
            account=recipient_account,
            amount=amount,
            balance_after_transaction=recipient_account.balance,
            transaction_type=TRANSACTION_TYPE_TRANSFER_IN
        )
        sent_transaction_mail(
            self.request.user,
            amount,
            'Money Transferred',
            'transactions/transferMoney_email.html'
        )
        sent_transaction_mail(
            recipient_account.user,
            amount,
            'Money Received',
            'transactions/transfer_received_email.html'
        )

        messages.success(self.request, 'Success: Money transferred.')
        
        return super().form_valid(form)