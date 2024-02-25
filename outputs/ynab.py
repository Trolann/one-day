from settings import YNAB_API_KEY, YNAB_BUDGET_ID
from requests import get, post, put, delete

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
        return get(f"{self.base_url}/budgets/{self.budget_id}/transactions",
                   params=params,
                   headers=self.headers).json()['data']['transactions']

# Program to convert strings representing negative amounts to float values

def convert_to_float(amount_str):
    try:
        # Convert string to float
        return float(amount_str) / 1000
    except ValueError as e:
        # Handle the case where conversion fails
        print(f"Error converting {amount_str} to float: {e}")
        return None



if __name__ == '__main__':
    from pprint import pprint
    ynab = YnabAPI()
    trans = ynab.get_uncategorized_amazon_transactions()
    pass