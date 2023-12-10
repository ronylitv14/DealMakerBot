import decimal
from typing import List
import io
import pandas as pd
from database.models import Transaction
from sqlalchemy.inspection import inspect
import csv

def transaction_to_tuple(transaction: Transaction) -> tuple:
    return tuple(getattr(transaction, attr.key) for attr in inspect(transaction).mapper.column_attrs)


def create_output_file_1(transactions: List[Transaction]):
    column_names = [
        "transaction_id",
        "invoice_id",
        "sender_id",
        "receiver_id",
        "task_id",
        "amount",
        "transaction_type",
        "transaction_status",
        "transaction_date"
    ]

    output = io.StringIO()  # Using StringIO for CSV data
    writer = csv.writer(output)

    # Write the column headers
    writer.writerow(column_names)

    # Write the transaction data
    for transaction in transactions:
        res = transaction_to_tuple(transaction)
        writer.writerow(res)

    output.seek(0)  # Rewind the buffer
    print(output.getvalue())  # For debugging, you can remove this line later

    # Convert StringIO to BytesIO for consistent return type
    return io.BytesIO(output.getvalue().encode())