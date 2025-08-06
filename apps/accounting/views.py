from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from decimal import Decimal
from apps.accounting.filters import TransactionFilter
from .models import AccountType, Account, JournalEntry, Transaction
from .serializers import (
    AccountTypeSerializer,
    AccountSerializer,
    CreateAccountSerializer,
    CreateAccountTypeSerializer,
    JournalEntrySerializer,
    TransactionSerializer,
)
from django.db.models import Sum
from collections import defaultdict
from datetime import datetime, date

from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend


# ----------------------
# ACCOUNT TYPES & ACCOUNTS
# ----------------------


class AccountTypeListView(generics.ListAPIView):
    queryset = AccountType.objects.all().order_by("-created_on")
    serializer_class = AccountTypeSerializer

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            account_types = self.get_queryset()
            account_types = self.filter_queryset(account_types)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_account_types = paginator.paginate_queryset(
                    account_types, request
                )
                serializer = self.get_serializer(paginated_account_types, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(account_types, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)


class ArchivedAccountTypeListView(generics.ListAPIView):
    queryset = AccountType.all_objects.filter(is_archived=True).order_by("-created_on")
    serializer_class = AccountTypeSerializer


class AccountTypeCreateAPIView(generics.CreateAPIView):
    queryset = AccountType.objects.all()
    serializer_class = CreateAccountTypeSerializer


class AccountTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccountType.objects.all()
    serializer_class = CreateAccountTypeSerializer
    lookup_field = "pk"

    def destroy(self, request, *args, **kwargs):
        account = self.get_object()
        account.is_archived = True
        account.save()
        return Response(
            {"message": "Account archived successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class AccountCreateAPIView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = CreateAccountSerializer


class AccountListAPIView(generics.ListAPIView):
    queryset = Account.objects.all().order_by("-created_on")
    serializer_class = AccountSerializer

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            accounts = self.get_queryset()
            accounts = self.filter_queryset(accounts)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_accounts = paginator.paginate_queryset(accounts, request)
                serializer = self.get_serializer(paginated_accounts, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(accounts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)


class ArchivedAccountListView(generics.ListAPIView):
    queryset = Account.all_objects.filter(is_archived=True).order_by("-created_on")
    serializer_class = AccountSerializer


class AccountDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = CreateAccountSerializer
    lookup_field = "pk"

    def destroy(self, request, *args, **kwargs):
        account = self.get_object()
        account.is_archived = True
        account.save()
        return Response(
            {"message": "Account archived successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class UnarchiveAccountView(APIView):
    def patch(self, request, pk):
        try:
            account = Account.all_objects.get(pk=pk)

        except Account.DoesNotExist:
            return Response(
                {"error": "Account not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not account.is_archived:
            return Response(
                {"message": "Account is already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        account.is_archived = False
        account.save()
        return Response(
            {"message": "Account unarchived successfully."}, status=status.HTTP_200_OK
        )


class UnarchiveAccountTypeView(APIView):
    def patch(self, request, pk):
        try:
            account_type = AccountType.all_objects.get(pk=pk)
        except AccountType.DoesNotExist:
            return Response({"error": "Account type not found."}, status=404)

        if not account_type.is_archived:
            return Response({"error": "Account type is already active."}, status=400)

        account_type.is_archived = False
        account_type.save()
        return Response(
            {"message": "Account type unarchived successfully."}, status=200
        )


# ----------------------
# JOURNAL ENTRIES
# ----------------------


class JournalEntryListCreateView(generics.ListCreateAPIView):
    queryset = JournalEntry.objects.all().prefetch_related("transactions").order_by("-created_on")

    serializer_class = JournalEntrySerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all().order_by("-created_on")
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TransactionFilter
    pagination_class = None

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            transactions = self.get_queryset()
            transactions = self.filter_queryset(transactions)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_transactions = paginator.paginate_queryset(
                    transactions, request
                )
                serializer = self.get_serializer(paginated_transactions, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)


# ----------------------
# TRIAL BALANCE
# ----------------------


class TrialBalanceView(APIView):
    def get(self, request):
        data = []
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        as_of_date_str = request.query_params.get("as_of_date")
        if as_of_date_str:
            try:
                as_of_date = datetime.strptime(as_of_date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."}, status=400
                )
        else:
            as_of_date = date.today()

        accounts = Account.objects.select_related("account_type")

        for account in accounts:
            # txs = account.transaction_set.all()
            # if start_date and end_date:
            #     txs = txs.filter(journal__date__range=[start_date, end_date])
            txs = account.transaction_set.filter(journal__date__lte=as_of_date)

            debits = txs.filter(is_debit=True).aggregate(Sum("amount"))[
                "amount__sum"
            ] or Decimal("0.00")
            credits = txs.filter(is_debit=False).aggregate(Sum("amount"))[
                "amount__sum"
            ] or Decimal("0.00")

            # Determine balance direction
            normal = account.account_type.normal_balance
            balance = debits - credits if normal == "debit" else credits - debits

            # Totals for footer
            total_debit += debits
            total_credit += credits

            data.append(
                {
                    "code": account.account_code,
                    "name": account.name,
                    "type": account.account_type.name,
                    "debit": float(debits),
                    "credit": float(credits),
                    "balance": float(balance),
                }
            )

        response = {
            "accounts": data,
            "totals": {
                "total_debit": float(total_debit),
                "total_credit": float(total_credit),
                "balanced": total_debit == total_credit,
            },
        }

        return Response(response)


# class TrialBalanceView(APIView):
#     def get(self, request):
#         from .models import Account
#         data = []
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
#         accounts = Account.objects.select_related("account_type")

#         for account in accounts:
#             txs = account.transaction_set.all()
#             if start_date and end_date:
#                 txs = txs.filter(journal__date__range=[start_date, end_date])

#             debits = txs.filter(is_debit=True).aggregate(Sum("amount"))["amount__sum"] or 0
#             credits = txs.filter(is_debit=False).aggregate(Sum("amount"))["amount__sum"] or 0

#             balance = debits - credits if account.account_type.normal_balance == "debit" else credits - debits

#             data.append({
#                 "code": account.account_code,
#                 "name": account.name,
#                 "type": account.account_type.name,
#                 "balance": balance
#             })

#         return Response(data)


# ----------------------
# BALANCE SHEET
# ----------------------
class BalanceSheetView(APIView):
    def get(self, request):
        as_of_date = request.query_params.get("as_of_date")
        sheet = {"Assets": [], "Liabilities": [], "Equity": []}
        total_income = Decimal("0.00")
        total_expenses = Decimal("0.00")

        for acc in Account.objects.select_related("account_type"):
            balance = get_account_balance(acc, as_of_date=as_of_date)
            balance = Decimal(str(balance or 0))  # Ensure Decimal

            account_type = acc.account_type.name
            account_data = {"name": acc.name, "balance": round(balance, 2)}

            if account_type == "Asset":
                sheet["Assets"].append(account_data)
            elif account_type == "Liability":
                sheet["Liabilities"].append(account_data)
            elif account_type == "Equity":
                sheet["Equity"].append(account_data)
            elif account_type == "Income":
                total_income += balance
            elif account_type == "Expense":
                total_expenses += balance

        # Add Retained Earnings to Equity
        net_income = total_income - total_expenses
        sheet["Equity"].append(
            {"name": "Retained Earnings", "balance": round(net_income, 2)}
        )

        # Totals for balance equation check
        total_assets = sum(item["balance"] for item in sheet["Assets"])
        total_liabilities = sum(item["balance"] for item in sheet["Liabilities"])
        total_equity = sum(item["balance"] for item in sheet["Equity"])

        sheet["Totals"] = {
            "Assets": round(total_assets, 2),
            "Liabilities + Equity": round(total_liabilities + total_equity, 2),
            "Balanced": total_assets == (total_liabilities + total_equity),
        }

        return Response(sheet)


# ----------------------
# INCOME STATEMENT
# ----------------------


class IncomeStatementView(APIView):
    def get(self, request):
        from .models import Account

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        income = []
        expenses = []

        for acc in Account.objects.select_related("account_type"):
            balance = get_account_balance(acc, start_date, end_date)
            if acc.account_type.name == "Income":
                income.append((acc.name, balance))
            elif acc.account_type.name == "Expense":
                expenses.append((acc.name, balance))

        # Calculate totals in backend
        total_income = sum(i[1] for i in income)
        total_expenses = sum(e[1] for e in expenses)
        net_profit = total_income - total_expenses

        # Calculate profit margin
        profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0

        return Response(
            {
                "income": [
                    {"name": name, "amount": balance} for name, balance in income
                ],
                "expenses": [
                    {"name": name, "amount": balance} for name, balance in expenses
                ],
                "totals": {
                    "total_income": total_income,
                    "total_expenses": total_expenses,
                    "net_profit": net_profit,
                    "profit_margin": round(profit_margin, 2),
                },
                "net_profit": net_profit,
            }
        )


# Utility
# def get_account_balance(account):
#     debits = account.transaction_set.filter(is_debit=True).aggregate(Sum("amount"))['amount__sum'] or 0
#     credits = account.transaction_set.filter(is_debit=False).aggregate(Sum("amount"))['amount__sum'] or 0

#     if account.account_type.normal_balance == 'debit':
#         return debits - credits
#     else:
#         return credits - debits


def get_account_balance(account, start_date=None, end_date=None, as_of_date=None):
    txs = account.transaction_set.all()
    if start_date and end_date:
        txs = txs.filter(journal__date__range=[start_date, end_date])
    elif as_of_date:
        txs = txs.filter(journal__date__lte=as_of_date)

    debits = txs.filter(is_debit=True).aggregate(Sum("amount"))["amount__sum"] or 0
    credits = txs.filter(is_debit=False).aggregate(Sum("amount"))["amount__sum"] or 0

    if account.account_type.normal_balance == "debit":
        return debits - credits
    else:
        return credits - debits


class CashFlowView(APIView):
    def get_opening_balance(self, start_date):
        # Filter only cash accounts
        cash_accounts = Account.objects.filter(account_type__name="Asset")
        transactions = Transaction.objects.filter(
            account__in=cash_accounts, journal__date__lt=start_date
        )
        inflow = (
            transactions.filter(is_debit=True).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        outflow = (
            transactions.filter(is_debit=False).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        return inflow - outflow

    def get(self, request):
        # Parse start_date and end_date from query params
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        try:
            start_date = (
                datetime.strptime(start_date_str, "%Y-%m-%d").date()
                if start_date_str
                else date.today()
            )
            end_date = (
                datetime.strptime(end_date_str, "%Y-%m-%d").date()
                if end_date_str
                else date.today()
            )
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."}, status=400
            )

        # Calculate the opening balance once before all sections
        opening_balance = self.get_opening_balance(start_date)

        # Define cash flow sections
        sections = {
            "Operating": Q(account__cash_flow_section="Operating"),
            "Investing": Q(account__cash_flow_section="Investing"),
            "Financing": Q(account__cash_flow_section="Financing"),
        }

        response_data = {}
        gross_inflows = Decimal("0.00")
        gross_outflows = Decimal("0.00")

        for section_name, filter_query in sections.items():
            transactions = (
                Transaction.objects.filter(
                    filter_query,
                    account__account_type__name="Asset",  # Only cash accounts
                    journal__date__range=(start_date, end_date),
                )
                .select_related("account", "journal")
                .order_by("journal__date")
            )

            journal_map = defaultdict(
                lambda: {
                    "journal_id": None,
                    "date": None,
                    "description": "",
                    "reference": "",
                    "transactions": [],
                }
            )

            section_inflows = Decimal("0.00")
            section_outflows = Decimal("0.00")

            for tx in transactions:
                journal = tx.journal
                key = journal.id

                if journal_map[key]["journal_id"] is None:
                    journal_map[key].update(
                        {
                            "journal_id": journal.id,
                            "date": journal.date,
                            "description": journal.description,
                            "reference": journal.reference,
                        }
                    )

                tx_type = "inflow" if tx.is_debit else "outflow"
                amount = tx.amount

                journal_map[key]["transactions"].append(
                    {"account": str(tx.account), "amount": str(amount), "type": tx_type}
                )

                if tx.is_debit:
                    section_inflows += amount
                else:
                    section_outflows += amount

            response_data[section_name] = {
                "journals": list(journal_map.values()),
                "totals": {
                    "inflows": str(section_inflows),
                    "outflows": str(section_outflows),
                    "net_cash_flow": str(section_inflows - section_outflows),
                },
            }

            gross_inflows += section_inflows
            gross_outflows += section_outflows

        # Final summary
        net_cash_change = gross_inflows - gross_outflows
        ending_balance = opening_balance + net_cash_change

        response_data["summary"] = {
            "opening_balance": str(opening_balance),
            "gross_inflows": str(gross_inflows),
            "gross_outflows": str(gross_outflows),
            "net_cash_change": str(net_cash_change),
            "ending_balance": str(ending_balance),
        }

        return Response(response_data)
