from settings import YNAB_API_KEY, YNAB_BUDGET_ID
from requests import get, post, put, delete
from inputs.amazon import AmazonTransactionFinder
from datetime import datetime

AMAZON_PAYEE_ID = '11454874-fb18-426d-b2e7-9babe4cb6875'


class YnabAPI:
    def __init__(self):
        self.base_url = 'https://api.ynab.com/v1/'
        self.headers = {"Authorization": f"Bearer {YNAB_API_KEY}"}
        self.budget_id = YNAB_BUDGET_ID
        self.amazon_finder = AmazonTransactionFinder(headless=True)

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

    def update_memo(self, transaction_id, amount, memo):
        # Print a debug statement about what would be added to the memo line
        print(f"Updating transaction for ${amount} with memo: {memo}")

        # Uncomment the following lines to actually update the memo in YNAB
        data = {
            "transaction": {
                "memo": memo[:199]
            }
        }
        url = f"{self.base_url}/budgets/{self.budget_id}/transactions/{transaction_id}"
        #print(data)
        response = put(url, json=data, headers=self.headers)
        #print(response.json())
        return response.json()

    def process_amazon_transactions(self):
        ynab_transactions = self.get_uncategorized_amazon_transactions()

        for ynab_trans in ynab_transactions:
            amount = ynab_trans['amount'] / 1000
            date = datetime.strptime(ynab_trans['date'], '%Y-%m-%d')

            amazon_trans = self.amazon_finder.find_transaction(amount, date, page_depth=5)

            if amazon_trans:
                memo = f"{amazon_trans['items']} ({amazon_trans['orderID']})"
                self.update_memo(ynab_trans['id'], amount, memo)
            else:
                print(f"No matching Amazon transaction found for YNAB transaction {ynab_trans['id']}")


if __name__ == '__main__':
    ynab = YnabAPI()
    ynab.process_amazon_transactions()