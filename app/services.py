import os
import pandas as pd
from datetime import datetime
from app.models import Transaction, ExportLog
from flask import jsonify

# Path where the generated Excel file will be saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')
if not os.path.exists(EXPORT_FOLDER):
    os.makedirs(EXPORT_FOLDER)

def save_transaction(data):
    required_fields = ['category', 'amount', 'currency', 'account']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return None, jsonify({'error': 'Missing fields', 'missing_fields': missing_fields})

    result = Transaction(**data)
    result.save()
    return result, ""

def get_new_transactions():
    """
    Fetch and process new transactions.
    """
    last_exported_id = ExportLog.get_last_exported_transaction_id()
    if last_exported_id:
        new_transactions_cursor = Transaction.get_new_transactions(last_exported_id)
    else:
        new_transactions_cursor = Transaction.get_all()
    new_transactions = list(new_transactions_cursor)
    if not new_transactions:
        return None
    save_export_log(new_transactions)

    processed_transactions = []
    for transaction in new_transactions:
        transaction['_id'] = str(transaction['_id'])  # Convert ObjectId to string
        transaction['amount'] = "{} {}".format(transaction['currency'], transaction['amount'])
        processed_transactions.append(transaction)

    return processed_transactions


def save_export_log(new_transactions):
    # Get the last transaction ID and update the export log
    last_transaction_id = str(new_transactions[-1]['_id'])
    ExportLog.save_last_exported_transaction_id(last_transaction_id)


def save_transactions_to_file(transactions):
    """
    Save processed transactions to a CSV file.
    """
    df = pd.DataFrame(transactions)
    file_path = os.path.join(EXPORT_FOLDER, "new_transactions_{}.csv".format(datetime.now().strftime("%Y%m%d%H%M%S")))
    df.to_csv(file_path, index=False, encoding='utf-8')
    return file_path


def withdraw_export_log():
    # Find the last export log
    last_export_log = ExportLog.get_last_log()

    if not last_export_log:
        return None

    ExportLog.delete_last_export(last_export_log["_id"])
    return last_export_log