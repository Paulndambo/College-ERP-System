from rest_framework import serializers
from .models import AccountType, Account, JournalEntry, Transaction


class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ["id", "name", "normal_balance"]


class CreateAccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ["name", "normal_balance"]

    def update(self, instance, validated_data):
        if "normal_balance" in validated_data:
            if instance.normal_balance != validated_data["normal_balance"]:
                if instance.account_set.exists():
                    raise serializers.ValidationError(
                        "Cannot change normal_balance of an AccountType that is already used by Accounts.This will alter the financial history."
                    )
        return super().update(instance, validated_data)


class AccountSerializer(serializers.ModelSerializer):
    account_type = AccountTypeSerializer(read_only=True)

    class Meta:
        model = Account
        fields = ["id", "account_code", "name", "account_type", "cash_flow_section"]


class CreateAccountSerializer(serializers.ModelSerializer):
    account_type = serializers.PrimaryKeyRelatedField(
        queryset=AccountType.objects.all(), write_only=True
    )
    is_default = serializers.BooleanField(default=False)
    is_contra = serializers.BooleanField(default=False)

    class Meta:
        model = Account
        fields = [
            "account_code",
            "name",
            "account_type",
            "is_contra",
            "is_default",
            "cash_flow_section",
        ]

    def validate_account_type(self, value):
        if value.is_archived:
            raise serializers.ValidationError("Cannot assign an archived account type.")
        return value

    def create(self, validated_data):
        account_type = validated_data["account_type"]
        validated_data["normal_balance"] = account_type.normal_balance
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)
    journal_info = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ["id", "account", "amount", "is_debit", "journal_info"]

    def get_journal_info(self, obj):
        return {
            "date": obj.journal.date,
            "description": obj.journal.description,
            "reference": obj.journal.reference,
        }


class CreateTransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), write_only=True
    )

    class Meta:
        model = Transaction
        fields = ["id", "account", "amount", "is_debit"]


class JournalEntrySerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True)

    class Meta:
        model = JournalEntry
        fields = [
            "id",
            "date",
            "description",
            "reference",
            "created_by",
            "transactions",
        ]
        read_only_fields = ["created_by"]

    def create(self, validated_data):
        transactions_data = validated_data.pop("transactions")
        journal_entry = JournalEntry.objects.create(**validated_data)

        total_debit = 0
        total_credit = 0

        for tx in transactions_data:
            is_debit = tx["is_debit"]
            amount = tx["amount"]
            if is_debit:
                total_debit += amount
            else:
                total_credit += amount

        if total_debit != total_credit:
            raise serializers.ValidationError("Debits and credits must be equal")

        for tx in transactions_data:
            Transaction.objects.create(journal=journal_entry, **tx)

        return journal_entry
