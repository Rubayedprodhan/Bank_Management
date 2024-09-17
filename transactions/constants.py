DEPOSIT = 1
WITHDRAWAL = 2
LOAN = 3
LOAN_PAID = 4
TRANSACTION_TYPE_TRANSFER_OUT = 5
TRANSACTION_TYPE_TRANSFER_IN = 6

TRANSACTION_TYPE = (
    (1, 'Deposite'),
    (2, 'Withdrawal'),
    (3, 'Load'),
    (4, 'Load paid'),
    (TRANSACTION_TYPE_TRANSFER_OUT, 'Transfer Out'),
    (TRANSACTION_TYPE_TRANSFER_IN, 'Transfer In'),
)