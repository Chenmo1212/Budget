import pandas as pd
import requests
import json

# API endpoint to save transactions
API_URL = "https://yourdomain/budget/transaction"  # Update this to your actual API endpoint

def read_csv_file(file_path):
    """
    Reads the CSV file and returns a DataFrame.
    :param file_path: Path to the CSV file.
    :return: pandas DataFrame
    """
    try:
        # Read CSV file into a DataFrame
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def save_transaction(transaction_data):
    """
    Calls the save transaction API to store transaction data.
    :param transaction_data: Dictionary containing transaction details.
    :return: API response or None if an error occurred.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        # Send POST request to API
        response = requests.post(API_URL, data=json.dumps(transaction_data), headers=headers)
        if response.status_code == 201:
            print(f"Transaction saved successfully: {transaction_data['description']}")
            return response.json()  # Return response JSON if successful
        else:
            print(f"Failed to save transaction: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error saving transaction: {e}")
        return None


def convert_currency_symbol(currency):
    """
    Converts currency symbols to ISO currency codes.
    :param currency: Currency symbol or code
    :return: ISO currency code
    """
    currency_map = {
        '€': 'EUR',
        '$': 'USD',
        '￥': 'CNY',
        '¥': 'CNY'  # ¥ is often used for both JPY and CNY, assuming CNY for this case
    }

    # If the currency is a symbol, replace it; otherwise return it as is
    return currency_map.get(currency, currency)


def process_and_upload_transactions(file_path):
    """
    Processes each transaction in the CSV file and uploads it via API.
    :param file_path: Path to the CSV file.
    """
    df = read_csv_file(file_path)

    if df is None:
        print("No data to process.")
        return

    # Iterate through the DataFrame row by row
    for _, row in df.iterrows():
        # Map the row data to the expected API format
        transaction_data = {
            "description": row["Description"] if pd.notna(row["Description"]) else None,
            "category": row["Category"],
            "amount": row["Cost"],
            "currency": convert_currency_symbol(row["Currency"]),
            "transaction_date": pd.to_datetime(row["Date"]).strftime('%Y-%m-%d'),  # Convert date to string
            "account": row["Account"],
            "payer": row["Payer"] if pd.notna(row["Payer"]) else None,
            "payee": row["Payee"] if pd.notna(row["Payee"]) else None
        }
        print(transaction_data)

        # Save each transaction by calling the API
        save_transaction(transaction_data)
        # break

if __name__ == "__main__":
    # Path to your CSV file
    csv_file_path = "transactions.csv"  # Update this to the path of your CSV file

    # Process and upload the transactions
    process_and_upload_transactions(csv_file_path)
