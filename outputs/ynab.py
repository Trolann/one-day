from settings import YNAB_API_KEY, YNAB_BUDGET_ID
from requests import get, post, put, delete
from inputs.amazon import load_prior_results

AMAZON_PAYEE_ID = '11454874-fb18-426d-b2e7-9babe4cb6875'

class YnabAPI:
    def __init__(self):
        self.base_url = 'https://api.ynab.com/v1/'
        self.headers = {"Authorization": f"Bearer {YNAB_API_KEY}"}
        self.budget_id = YNAB_BUDGET_ID

    def get_budgets(self):
        return get(f"{self.base_url}/budgets", headers=self.headers).json()

    def get_uncategorized_amazon_transactions(self):
        params = {
            "type": "unapproved"
        }
        transactions = get(f"{self.base_url}/budgets/{self.budget_id}/transactions",
                           headers=self.headers,
                           params=params).json()['data']['transactions']
        return [t for t in transactions if t['payee_id'] == AMAZON_PAYEE_ID]

# Program to convert strings representing negative amounts to float values

def convert_to_float(amount_str):
    try:
        # Convert string to float
        return float(amount_str) / 1000
    except ValueError as e:
        # Handle the case where conversion fails
        print(f"Error converting {amount_str} to float: {e}")
        return None

def pair_transactions(ynab_transactions, amazon_transactions):
    # Convert ynab transaction amounts to float and map them for easy access
    ynab_amounts = {convert_to_float(t['amount']): t['id'] for t in ynab_transactions}
    paired_transactions = []

    for amazon_transaction in amazon_transactions:
        # Convert amazon transaction amount to match ynab format (negative for expenses)
        amazon_amount = -amazon_transaction['amount']
        if amazon_amount in ynab_amounts:
            paired_transactions.append({
                'ynab_transaction_id': ynab_amounts[amazon_amount],
                'transaction_amount': amazon_amount,
                'items': ''.join(amazon_transaction['items']), #amazon_transaction['items'],
                'amazon_order_id': amazon_transaction['orderID']
            })

    return paired_transactions

if __name__ == '__main__':
    from pprint import pprint
    ynab = YnabAPI()
    ynab_transactions = ynab.get_uncategorized_amazon_transactions()
    amazon_transactions = load_prior_results(id_only=False)
    paired_transactions = pair_transactions(ynab_transactions, amazon_transactions)
    pprint([t['items'] for t in paired_transactions])
    print(f'Had {len(amazon_transactions)} amazon transactions')
    print(f'Had {len(ynab_transactions)} ynab transactions')
    print(f'Found {len(paired_transactions)} paired transactions')
    print(f'Paired {(len(paired_transactions) / len(ynab_transactions)) * 100}% of transactions')
    bad_trans_ids = []
    for transact in ynab_transactions:
        # if not in paired_transactions, print it
        if transact['id'] not in [t['ynab_transaction_id'] for t in paired_transactions]:
            print(f"{transact}")
