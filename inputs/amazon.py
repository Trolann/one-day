#amazon.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
from anthropic import Client
from anthropic.types.tool_param import ToolParam
from settings import AMAZON_LOGIN, AMAZON_PASSWORD, OPUS, SONNET, HAIKU
from datetime import datetime

class AmazonTransactionFinder:

    def __init__(self, headless=True):
        self.client = Client()
        self.MODEL = HAIKU
        self.driver = self.initialize_driver(headless)
        transaction_map = {
            "name": "transaction_map",
            "description": "Map details of a transaction to add to bank ledger memo line",
            "input_schema": {
                "type": "object",
                "properties": {
                    "orderID": {
                        "type": "string",
                        "description": "Unique identifier for the transaction (copy paste from the given text)"
                    },
                    "amount": {
                        "type": "number",
                        "description": "The transaction amount (copy paste from the given text)"
                    },
                    "items": {
                        "type": "string",
                        "description": "A very concise description of the entire order represented by the transcation."
                                       "No more than 10-12 words, no deep descriptions of the items."
                                       "Examples: 'Kitchen Shears, 2x T-Shirts', 'Valentines Day cards and decorations'"
                                       ", 'Goodnight Moon book, baby onesies and stacking blocks.'"
                    },
                    "transaction_date": {
                        "type": "string",
                        "description": "The date and time when the transaction was made. In the format 'Month DD, YYYY'"
                                       "and will be extracted by "
                                       "`datetime.strptime(transaction['transaction_date'], '%B %d, %Y')`"
                    }
                },
                "required": ["orderID", "amount", "items", "transaction_date"]
            }
        }
        self.tools = [ToolParam(**transaction_map)]
        self.login()

    def initialize_driver(self, headless):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def login(self):
        self.driver.get("https://www.amazon.com/gp/sign-in.html")
        self.driver.find_element(By.ID, "ap_email").send_keys(AMAZON_LOGIN)
        self.driver.find_element(By.ID, "continue").click()
        sleep(2)
        self.driver.find_element(By.ID, "ap_password").send_keys(AMAZON_PASSWORD)
        self.driver.find_element(By.ID, "signInSubmit").click()

        try:
            self.driver.find_element(By.NAME, "cvf_captcha_input")
            self.driver.save_screenshot('captcha.png')
            captcha = input("Please solve the captcha and press enter to continue:\n")
            self.driver.find_element(By.NAME, "cvf_captcha_input").send_keys(captcha)
            self.driver.find_element(By.NAME, "cvf_captcha_captcha_action").click()
        except:
            pass

    def find_transaction(self, amount, date, page_depth=5):
        trans_url = "https://www.amazon.com/cpe/yourpayments/transactions"
        self.driver.get(trans_url)
        total_height = self.driver.execute_script("return document.body.parentNode.scrollHeight")
        window_height = total_height - (580 * 2)
        window_height = window_height if window_height > 0 else total_height
        self.driver.set_window_size(225, window_height)

        closest_transaction = None
        closest_date_diff = float('inf')

        for p in range(page_depth):
            sleep(5)
            self.driver.execute_script("window.scrollTo(0, 0);")

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            transaction_text = soup.get_text()
            order_ids = self.find_order_ids_by_amount(soup, amount)

            for order_id in order_ids:
                transaction = self.get_transaction_details(order_id)
                if transaction:
                    try:
                        trans_date = datetime.strptime(transaction['transaction_date'], '%B %d, %Y')
                    except ValueError:
                        # try YYYY-MM-DD format
                        try:
                            trans_date = datetime.strptime(transaction['transaction_date'], '%Y-%m-%d')
                        except ValueError:
                            # transaction was today
                            trans_date = datetime.now()
                    date_diff = abs((date - trans_date).days)
                    if date_diff < closest_date_diff:
                        closest_transaction = transaction
                        closest_date_diff = date_diff

            try:
                find_value = "//input[contains(@name, 'DefaultNextPageNavigationEvent')]"
                next_page_button = self.driver.find_element(By.XPATH, find_value)
                next_page_button.click()
            except Exception as e:
                #print(f"Error: {e}")
                break

        return closest_transaction

    def find_order_ids_by_amount(self, soup, target_amount):
        order_ids = []
        spans = soup.find_all('span', class_='a-size-base-plus')
        for span in spans:
            if span.parent.name == 'div' and span.parent.get('class') == ['a-column', 'a-span3', 'a-text-right',
                                                                          'a-span-last']:
                amount_str = span.text.replace('$', '').replace(',', '')
                if amount_str.startswith('-'):
                    amount_str = amount_str[1:]
                if float(amount_str) == abs(target_amount):
                    link = span.parent.parent.find_next_sibling('div').find('a')
                    if link:
                        order_id = link['href'].split('orderID=')[1]
                        order_ids.append(order_id)
        return order_ids

    def get_transaction_details(self, order_id):
        if order_id.startswith('D'):
            trans_url = f'https://www.amazon.com/gp/css/order-details?orderID={order_id}'
        else:
            trans_url = f'https://www.amazon.com/gp/css/summary/edit.html?orderID={order_id}'

        self.driver.get(trans_url)
        sleep(2)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        start_idx = soup.get_text().find("Ordered on ") + 11
        end_idx = soup.get_text().find('Buy it again')
        #transaction_text = soup.get_text()[start_idx:end_idx]
        transaction_text = soup.get_text()[start_idx:]
        clean_text = '\n'.join([line for line in transaction_text.split('\n') if line.strip() != ''])

        if 'Something went wrong, please sign-in' not in clean_text:
            return self.parse_transaction_text(clean_text, order_id)
        else:
            print('Something went wrong, please sign-in')
            return None

    def parse_transaction_text(self, text, order_id):
        messages = [{"role": "user", "content": f"Request:\n{text}"}]
        print('Calling Claude')
        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=4096,
            tools=self.tools,
            messages=messages
        )

        retries_left = 3 if response.stop_reason != "tool_use" else 0
        while retries_left:
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": "This is incorrect, respond with a tool call. "
                                                        "Please provide a tool call"})
            retries_left -= 1
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=4096,
                tools=self.tools,
                messages=[
                    {"role": "system", "content": "Please provide a tool call"}
                ]
            )

        for tool_call in [block for block in response.content if block.type == "tool_use"]:
            function_name = tool_call.name
            item = tool_call.input
            if type(tool_call.input) is not dict:
                try:
                    item = eval(str(tool_call.input))
                except Exception as e:
                    print(f'Error: {e}')
                    print(f'Line: {tool_call.input}')
                    continue
            item['orderID'] = order_id
            return item

        return None


if __name__ == '__main__':
    hd = True
    finder = AmazonTransactionFinder(headless=hd)

    # Example usage
    amount = 25.22
    date = datetime(2024, 3, 18)
    result = finder.find_transaction(amount, date, page_depth=5)

    if result:
        print(f"Transaction found: {result}")
    else:
        print("Transaction not found")