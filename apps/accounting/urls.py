from django.urls import path
from .views import (
    AccountCreateAPIView,
    AccountDetailAPIView,
    AccountTypeCreateAPIView,
    AccountTypeDetailView,
    AccountTypeListView,
    AccountListAPIView,
    ArchivedAccountListView,
    ArchivedAccountTypeListView,
    CashFlowView,
    JournalEntryListCreateView,
    TransactionListView,
    TrialBalanceView,
    BalanceSheetView,
    IncomeStatementView,
    UnarchiveAccountTypeView,
    UnarchiveAccountView,
)

urlpatterns = [
    path("account-types/", AccountTypeListView.as_view(), name="account-types"),
    path(
        "account-types/create/",
        AccountTypeCreateAPIView.as_view(),
        name="create-account-types",
    ),
    path(
        "account-types/<int:pk>/",
        AccountTypeDetailView.as_view(),
        name="view-update-delete-account-types",
    ),
    path("", AccountListAPIView.as_view(), name="accounts"),
    path("cashflow/", CashFlowView.as_view(), name="cashflow"),
    path("transactions/", TransactionListView.as_view(), name="transactions"),
    path("archived/", ArchivedAccountListView.as_view(), name="archived-accounts"),
    path(
        "account-types/archived/",
        ArchivedAccountTypeListView.as_view(),
        name="archived-account-types",
    ),
    path(
        "<int:pk>/unarchive/", UnarchiveAccountView.as_view(), name="unarchive-account"
    ),
    path(
        "account-types/<int:pk>/unarchive/",
        UnarchiveAccountTypeView.as_view(),
        name="unarchive-account-type",
    ),
    path("create/", AccountCreateAPIView.as_view(), name="create-accounts"),
    path(
        "<int:pk>/", AccountDetailAPIView.as_view(), name="view-update-delete-account"
    ),
    path(
        "journal-entries/", JournalEntryListCreateView.as_view(), name="journal-entries"
    ),
    path("trial-balance/", TrialBalanceView.as_view(), name="trial-balance"),
    path("balance-sheet/", BalanceSheetView.as_view(), name="balance-sheet"),
    path("income-statement/", IncomeStatementView.as_view(), name="income-statement"),
]
