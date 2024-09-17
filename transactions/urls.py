from django.urls import path
from . import views
urlpatterns = [
    path("deposit/", views.DepositMoneyViews.as_view(), name='deposit_money'),
    path("withraw/", views.WithdrawMoneyViews.as_view(), name='withdraw_money'),
    path("report/", views.TransactionReportView.as_view(), name='transaction_report'),
    path("loan/request/", views.LoanRequestViews.as_view(), name='loan_request'),
    path("loans/", views.LoanListView.as_view(), name='loan_list'),
    path("loan/<int:loan_id>/", views.PayLoanView.as_view(), name='payloan'),
    path("transfer_money/", views.TransferMoneyView.as_view(), name='transfer_money')
]
