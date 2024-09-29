from app import mongo
from datetime import datetime
from bson import ObjectId


class Transaction:
    def __init__(self, description, category, amount, currency, transaction_date, account, payer, payee,
                 create_time=None, update_time=None, id=None):
        self.id = ObjectId(id) if id else None
        self.description = description  # Description
        self.category = category  # Category
        self.amount = amount #Amount
        self.currency = currency  # Currency
        self.transaction_date = transaction_date  # Transaction date
        self.account = account  # Account
        self.payer = payer  # Payer
        self.payee = payee  # Payee
        self.create_time = create_time or datetime.now()  # creation time
        self.update_time = update_time or datetime.now()  # Update time

    def save(self):
        """Save or update transaction history"""
        current_time = datetime.now()
        data = {
            'description': self.description,
            'category': self.category,
            'amount': self.amount,
            'currency': self.currency,
            'transaction_date': self.transaction_date,
            'account': self.account,
            'payer': self.payer,
            'payee': self.payee,
            'create_time': self.create_time,
            'update_time': self.update_time or current_time
        }

        if self.id:
            # Update existing records
            mongo.db.transactions.update_one({'_id': ObjectId(self.id)}, {'$set': data})
        else:
            # Insert new record
            result = mongo.db.transactions.insert_one(data)
            self.id = str(result.inserted_id)

        return str(self.id)

    def delete(self):
        """Delete transaction history"""
        if self.id:
            mongo.db.transactions.delete_one({'_id': ObjectId(self.id)})

    @staticmethod
    def get_all():
        """Get all transaction records"""
        return mongo.db.transactions.find()

    @staticmethod
    def get_by_id(transaction_id):
        """Get transaction records based on ID"""
        return mongo.db.transactions.find_one({'_id': ObjectId(transaction_id)})

    @staticmethod
    def get_new_transactions(since_id):
        """Get new transactions since the last exported transaction ID"""
        if isinstance(since_id, str):
            since_id = ObjectId(since_id)
        return mongo.db.transactions.find({'_id': {'$gt': since_id}})


class ExportLog:
    @staticmethod
    def get_last_exported_transaction_id():
        """Retrieve the last exported transaction ID"""
        last_export = mongo.db.export_log.find_one(sort=[("exported_transaction_id", -1)])
        return last_export['exported_transaction_id'] if last_export else None

    @staticmethod
    def save_last_exported_transaction_id(transaction_id):
        """Save the last exported transaction ID to the export_log collection"""
        mongo.db.export_log.insert_one({
            'exported_transaction_id': ObjectId(transaction_id),
            'exported_at': datetime.now()  # Optional timestamp for audit purposes
        })