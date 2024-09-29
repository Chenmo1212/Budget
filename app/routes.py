from flask import jsonify, request, send_file
from app import app
from dotenv import load_dotenv
from app.services import get_new_transactions, save_transactions_to_file, save_transaction

load_dotenv()


@app.route('/', methods=['GET'])
def index():
    return "hello world"


# This API saves a new transaction and returns its ID.
@app.route('/budget/transaction', methods=['POST'])
def save():
    result = save_transaction(request.json)
    return jsonify({
        'message': 'Transaction saved successfully',
        'transaction_id': str(result.id)
    }), 201  # 201 status code indicates that the resource has been created


# This API exports new transactions as JSON data.
@app.route('/budget/export', methods=['GET'])
def export_new_transactions():
    new_transactions = get_new_transactions()
    if not new_transactions:
        return jsonify({"message": "No new transactions to export"}), 201

    return jsonify({
        "data": new_transactions,
    }), 200


# This API exports new transactions and sends them as a CSV file.
@app.route('/budget/export_file', methods=['GET'])
def export_new_transactions_file():
    new_transactions = get_new_transactions()
    if not new_transactions:
        return jsonify({"message": "No new transactions to export"}), 201

    file_path = save_transactions_to_file(new_transactions)
    return send_file(file_path, as_attachment=True)