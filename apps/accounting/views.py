# from rest_framework import generics
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from .models import AccountType, Account, JournalEntry
# from .serializers import (
#     AccountTypeSerializer,
#     AccountSerializer,
#     JournalEntrySerializer,
# )
# from django.db.models import Sum


# # ----------------------
# # ACCOUNT TYPES & ACCOUNTS
# # ----------------------

# class AccountTypeListView(generics.ListAPIView):
#     queryset = AccountType.objects.all()
#     serializer_class = AccountTypeSerializer


# class AccountListCreateView(generics.ListCreateAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountSerializer


# # ----------------------
# # JOURNAL ENTRIES
# # ----------------------

# class JournalEntryListCreateView(generics.ListCreateAPIView):
#     queryset = JournalEntry.objects.all().prefetch_related('transactions')
    
#     serializer_class = JournalEntrySerializer

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)


# # ----------------------
# # TRIAL BALANCE
# # ----------------------

# class TrialBalanceView(APIView):
#     def get(self, request):
#         from .models import Account
#         data = []
#         accounts = Account.objects.select_related("account_type")

#         for account in accounts:
#             debits = account.transaction_set.filter(is_debit=True).aggregate(Sum("amount"))["amount__sum"] or 0
#             credits = account.transaction_set.filter(is_debit=False).aggregate(Sum("amount"))["amount__sum"] or 0
#             if account.account_type.normal_balance == "debit":
#                 balance = debits - credits
#             else:
#                 balance = credits - debits

#             data.append({
#                 "code": account.code,
#                 "name": account.name,
#                 "type": account.account_type.name,
#                 "balance": balance
#             })

#         return Response(data)


# # ----------------------
# # BALANCE SHEET
# # ----------------------

# class BalanceSheetView(APIView):
#     def get(self, request):
#         from .models import Account
#         sheet = {"Assets": [], "Liabilities": [], "Equity": []}

#         for acc in Account.objects.select_related("account_type"):
#             balance = get_account_balance(acc)
#             if acc.account_type.name == "Asset":
#                 sheet["Assets"].append((acc.name, balance))
#             elif acc.account_type.name == "Liability":
#                 sheet["Liabilities"].append((acc.name, balance))
#             elif acc.account_type.name == "Equity":
#                 sheet["Equity"].append((acc.name, balance))

#         return Response(sheet)


# # ----------------------
# # INCOME STATEMENT
# # ----------------------

# class IncomeStatementView(APIView):
#     def get(self, request):
#         from .models import Account
#         income = []
#         expenses = []

#         for acc in Account.objects.select_related("account_type"):
#             balance = get_account_balance(acc)
#             if acc.account_type.name == "Income":
#                 income.append((acc.name, balance))
#             elif acc.account_type.name == "Expense":
#                 expenses.append((acc.name, balance))

#         net_profit = sum(i[1] for i in income) - sum(e[1] for e in expenses)

#         return Response({
#             "Income": income,
#             "Expenses": expenses,
#             "NetProfit": net_profit
#         })


# # Utility
# def get_account_balance(account):
#     debits = account.transaction_set.filter(is_debit=True).aggregate(Sum("amount"))['amount__sum'] or 0
#     credits = account.transaction_set.filter(is_debit=False).aggregate(Sum("amount"))['amount__sum'] or 0

#     if account.account_type.normal_balance == 'debit':
#         return debits - credits
#     else:
#         return credits - debits
