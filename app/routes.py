from flask import jsonify, request, send_file, render_template
from app import app
from dotenv import load_dotenv
from app.services import get_new_transactions, save_transactions_to_file, save_transaction, withdraw_export_log

load_dotenv()


@app.route('/budget/', methods=['GET'])
def index():
    return render_template('index.html')


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
@app.route('/budget/export/file', methods=['GET'])
def export_new_transactions_file():
    new_transactions = get_new_transactions()
    if not new_transactions:
        return jsonify({"message": "No new transactions to export"}), 201

    file_path = save_transactions_to_file(new_transactions)
    return send_file(file_path, as_attachment=True)


# API to withdraw the last export log
@app.route('/budget/log', methods=['DELETE'])
def withdraw_last_export():
    last_export_log = withdraw_export_log()

    if not last_export_log:
        return jsonify({"message": "No export log entries found to withdraw."}), 404

    return jsonify({
        "message": "Last export log entry has been successfully withdrawn.",
        "export_log_id": str(last_export_log["_id"])
    }), 200
