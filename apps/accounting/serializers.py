# from rest_framework import serializers
# from .models import AccountType, Account, JournalEntry, Transaction


# class AccountTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AccountType
#         fields = ['id', 'name', 'normal_balance']


# class AccountSerializer(serializers.ModelSerializer):
#     account_type = AccountTypeSerializer(read_only=True)
#     account_type_id = serializers.PrimaryKeyRelatedField(
#         queryset=AccountType.objects.all(), source='account_type', write_only=True
#     )

#     class Meta:
#         model = Account
#         fields = ['id', 'code', 'name', 'account_type', 'account_type_id']


# class TransactionSerializer(serializers.ModelSerializer):
#     account = AccountSerializer(read_only=True)
#     account_id = serializers.PrimaryKeyRelatedField(
#         queryset=Account.objects.all(), source='account', write_only=True
#     )

#     class Meta:
#         model = Transaction
#         fields = ['id', 'account', 'account_id', 'amount', 'is_debit']


# class JournalEntrySerializer(serializers.ModelSerializer):
#     transactions = TransactionSerializer(many=True)

#     class Meta:
#         model = JournalEntry
#         fields = ['id', 'date', 'description', 'reference', 'created_by', 'transactions']
#         read_only_fields = ['created_by']

#     def create(self, validated_data):
#         transactions_data = validated_data.pop('transactions')
#         journal_entry = JournalEntry.objects.create(**validated_data)

#         total_debit = 0
#         total_credit = 0

#         for tx in transactions_data:
#             is_debit = tx['is_debit']
#             amount = tx['amount']
#             if is_debit:
#                 total_debit += amount
#             else:
#                 total_credit += amount

#         if total_debit != total_credit:
#             raise serializers.ValidationError("Debits and credits must be equal")

#         for tx in transactions_data:
#             Transaction.objects.create(journal=journal_entry, **tx)

#         return journal_entry
