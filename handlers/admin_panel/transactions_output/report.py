import io
import csv

from database_api.components.transactions import TransactionModel, TransactionList


def transaction_to_tuple(transaction: TransactionModel) -> tuple:
    return tuple(getattr(transaction, field) for field in transaction.model_fields)


def create_output_file(transactions: TransactionList):
    column_names = [
        "transaction_id",
        "invoice_id",
        "sender_id",
        "receiver_id",
        "task_id",
        "amount",
        "commission",
        "transaction_type",
        "transaction_status",
        "transaction_date"
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(column_names)

    for transaction in transactions:
        res = transaction_to_tuple(transaction)
        writer.writerow(res)

    output.seek(0)
    return io.BytesIO(output.getvalue().encode(encoding="utf-8"))
