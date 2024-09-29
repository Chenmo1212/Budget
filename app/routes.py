from flask import jsonify, request, send_file
from app import app, mongo
from app.models import Transaction, ExportLog
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@app.route('/', methods=['GET'])
def index():
    return "hello world"


@app.route('/budget/transaction', methods=['POST'])
def save_transaction():
    data = request.json

    required_fields = ['description', 'category', 'amount', 'currency', 'transaction_date', 'account', 'payer', 'payee']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': 'Missing fields', 'missing_fields': missing_fields}), 400

    result = Transaction(**data)
    result.save()

    return jsonify({
        'message': 'Transaction saved successfully',
        'transaction_id': str(result.id)
    }), 201  # 201 status code indicates that the resource has been created


# Path where the generated Excel file will be saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')
if not os.path.exists(EXPORT_FOLDER):
    os.makedirs(EXPORT_FOLDER)


@app.route('/budget/export', methods=['GET'])
def export_new_transactions():
    new_transactions, file_path = get_new_transactions()
    server_path = file_path.replace('/www/wwwroot/', '')
    return jsonify({
        "path": server_path,
        "new_transactions": new_transactions,
        "length": len(new_transactions)
    }), 200


@app.route('/budget/export_file', methods=['GET'])
def export_new_transactions_file():
    _, file_path = get_new_transactions()
    return send_file(file_path, as_attachment=True)


def get_new_transactions():
    last_exported_id = ExportLog.get_last_exported_transaction_id()
    if last_exported_id:
        new_transactions_cursor = Transaction.get_new_transactions(last_exported_id)
    else:
        new_transactions_cursor = Transaction.get_all()

    new_transactions = list(new_transactions_cursor)
    if not new_transactions:
        return jsonify({"message": "No new transactions to export"}), 200

    processed_transactions = []
    for transaction in new_transactions:
        transaction['amount'] = f"{transaction['currency']} {transaction['amount']}"  # Combine currency and amount
        processed_transactions.append(transaction)
    df = pd.DataFrame(processed_transactions)
    file_path = os.path.join(EXPORT_FOLDER, f'new_transactions_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx')
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, index=False, engine='xlsxwriter')

    last_transaction_id = str(new_transactions[-1]['_id'])
    ExportLog.save_last_exported_transaction_id(last_transaction_id)

    return new_transactions, file_path


# def post_wx(obj):
#     try:
#         CORPID = os.getenv('CORPID')  # enterprise id
#         AGENTID = os.getenv('AGENTID')  # application id
#         CORPSECRET = os.getenv('CORPSECRET')  # application secret
#
#         get_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORPID}&corpsecret={CORPSECRET}"
#         response = requests.get(get_token_url).content
#         access_token = json.loads(response).get('access_token')
#
#         if access_token and len(access_token) > 0:
#             send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
#             data = {
#                 "touser": '@all',
#                 "agentid": AGENTID,
#                 "msgtype": "textcard",
#                 "textcard": {
#                     "title": "Home message",
#                     "description": obj['content'],
#                     "url": os.getenv('ADMINURL'),
#                     "btntxt": "More"
#                 },
#                 "enable_id_trans": 0,
#                 "enable_duplicate_check": 0,
#                 "duplicate_check_interval": 1800
#             }
#             res = requests.post(send_msg_url, data=json.dumps(data))
#             return {'msg': 'Failed to post wechat notification.', 'status': res.status_code}
#         else:
#             return {'error': 'Failed to post wechat notification. access_token is invalid.', 'status': 500}
#     except Exception as e:
#         return {'error': 'Failed to post wechat notification.' + str(e), 'status': 500}
