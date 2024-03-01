from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pickle import dump, load
from time import sleep
from os import remove, listdir, path
from bs4 import BeautifulSoup
from multiprocessing import Pool
from openai import OpenAI
from settings import OPENAI_API_KEY, amazon_user_prompt
from json import loads
from settings import AMAZON_LOGIN, AMAZON_PASSWORD, AMAZON_ASSISTANT_ID

client = OpenAI(api_key=OPENAI_API_KEY)

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def show_json(obj):
    print(loads(obj.model_dump_json()))

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        sleep(0.5)
    return run


def parse_amazon_text(text: str, orderid: str) -> dict | None:
    if 'prime student fee' in text.lower():
        return {
            'orderID': orderid,
            'amount': 8.17,
            'items': 'Prime Student Fee'
        }
    thread = client.beta.threads.create()
    assistant = client.beta.assistants.retrieve(AMAZON_ASSISTANT_ID)
    print(f'Starting run for orderID: {orderid}')
    run = client.beta.threads.runs.create(thread_id=thread.id,
                                          assistant_id=assistant.id,
                                          instructions=text + '\n' + amazon_user_prompt)

    run = wait_on_run(run, thread)

    run_results = loads(run.model_dump_json())

    print(f'Got run for orderID: {orderid}')
    try:
        # TODO: Ensure only 1 entry per orderid
        result_dict = loads(run_results['required_action']['submit_tool_outputs']['tool_calls'][0]['function']['arguments'])
    except TypeError:
        print(f'Error parsing run for orderID: {orderid}')
        try:
            with('error.txt', 'a') as f:
                f.write(f'Error parsing run for orderID: {orderid}')
        except FileNotFoundError:
            with('error.txt', 'w') as f:
                f.write(f'Error parsing run for orderID: {orderid}')
        return None
    print(f'Writing results for orderID: {orderid}')
    # TODO: replace with a database
    with open('amazon.json', 'a') as f:
        f.write(str(result_dict))
        f.write('\n')

    return result_dict

def login(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.amazon.com/gp/sign-in.html")
    # Step 2: Automate login (Replace 'your_email' and 'your_password' with your Amazon credentials)
    driver.find_element(By.ID, "ap_email").send_keys(AMAZON_LOGIN)
    driver.find_element(By.ID, "continue").click()
    sleep(2)  # Wait for page load
    driver.find_element(By.ID, "ap_password").send_keys(AMAZON_PASSWORD)
    driver.find_element(By.ID, "signInSubmit").click()

    try:
        # See if the text is on the screen
        driver.find_element(By.NAME, "cvf_captcha_input")
        driver.save_screenshot('captcha.png')
        captcha = input("Please solve the captcha and press enter to continue:\n")
        driver.find_element(By.NAME, "cvf_captcha_input").send_keys(captcha)
        driver.find_element(By.NAME, "cvf_captcha_captcha_action").click()
    except:
        pass


    # Delete cookie from disk
    try:
        remove("amazon_cookies.pkl")
    except FileNotFoundError:
        pass

    # Step 3: Save cookies for later use
    dump(driver.get_cookies(), open("amazon_cookies.pkl", "wb"))
    driver.quit()


def worker_init():
    # This function will be called by each worker process once
    global cookies
    cookies = load(open("amazon_cookies.pkl", "rb"))


def get_trans_list(headless=False):
    trans_url = "https://www.amazon.com/cpe/yourpayments/transactions"
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    parse_driver = webdriver.Chrome(options=chrome_options)
    parse_driver.get('https://www.amazon.com')
    _cookies = load(open("amazon_cookies.pkl", "rb"))
    for cookie in _cookies:
        parse_driver.add_cookie(cookie)

    parse_driver.get(trans_url)
    total_height = parse_driver.execute_script("return document.body.parentNode.scrollHeight")
    window_height = total_height - (580 * 2)
    window_height = window_height if window_height > 0 else total_height
    parse_driver.set_window_size(225, window_height)

    image_strings = []
    pages = 0
    for page in range(1, 3):
        sleep(5)
        print(f'Parsing page {page}')
        # Save a screenshot (for debugging)
        parse_driver.execute_script("window.scrollTo(0, 0);")
        parse_driver.save_screenshot(f'page_{page}.png')
        print(f'Saved screenshot of page {page}')
        pages = page
        #image = Image.open(f'page_{page}.png')
        #image = image.crop((25, 330, 300, total_height - (580 * 2)))
        #image_strings.append(image_to_string(image))

        trans_list_soup = BeautifulSoup(parse_driver.page_source, 'html.parser')
        image_strings.append(trans_list_soup.get_text())

        # click "Next Page" button
        try:
            find_value = "//input[contains(@name, 'DefaultNextPageNavigationEvent')]"
            next_page_button = parse_driver.find_element(By.XPATH, find_value)
            next_page_button.click()
        except Exception as e:
            print(f"Error: {e}")
            continue

    parse_driver.quit()
    # Extract every unique string which is:
    # 113-1173472-3274645
    # that is 3 characters, a hyphen, 7 characters, a hyphen, and 7 characters
    print('Getting matches')
    matches = find_matching_substrings(image_strings)
    print(matches)
    # delete the screenshots
    #for page in range(1, pages + 1):
    #    remove(f'page_{page}.png')

    return matches

def find_matching_substrings(strings):
    # Define the pattern for 3 characters, a hyphen, 7 characters, a hyphen, and 3 characters
    all_matches = set()

    for i, string in enumerate(strings):
        print(f'Parsing string {i} of {len(strings)}')
        start_idx = 0
        while string.find('Order #', start_idx) != -1:
            start_idx = string.find('Order #', start_idx) + 7
            stripped_match = string[start_idx:start_idx+19].strip()
            stripped_match = stripped_match.strip('\n')
            all_matches.add(stripped_match)
            start_idx += 20

    return list(all_matches)


def parse_trans(transaction_id: str) -> None:
    if transaction_id.startswith('D'):
        trans_url = f'https://www.amazon.com/gp/css/order-details?orderID={transaction_id}'
    else:
        trans_url = f'https://www.amazon.com/gp/css/summary/edit.html?orderID={transaction_id}'

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    parse_driver = webdriver.Chrome(options=chrome_options)

    parse_driver.get('https://www.amazon.com')
    for cookie in cookies:
        parse_driver.add_cookie(cookie)

    parse_driver.get(trans_url)
    sleep(2)
    soup = BeautifulSoup(parse_driver.page_source, 'html.parser')
    parse_driver.quit()
    start_idx = soup.get_text().find("Ordered on ") + 11
    end_idx = soup.get_text().find('Buy it again')
    small_soup = soup.get_text()[start_idx:end_idx]
    clean_soup = '\n'.join([line for line in small_soup.split('\n') if line.strip() != ''])
    # write the clean_soup to a file for debugging
    with open(f'clean_soup/{transaction_id}.txt', 'w') as f:
        f.write(clean_soup)

    if 'Something went wrong, please sign-in' not in clean_soup:
        #parse_amazon_text(clean_soup, transaction_id)
        pass
    else:
        print('Something went wrong, please sign-in')

def load_prior_results(id_only=True):
    # {'orderID': '111-8079947-6269031', 'amount': 81.83, 'items': 'Computer Monitor'}
    # Iterate line by line. We need to returna a list of strings containing orderID only
    return_list = []
    try:
        with open('amazon.json', 'r') as f:
            for i, line in enumerate(f):
                # i used for debug counter
                try:
                    line_dict = eval(line)
                    return_list.append(line_dict)
                except Exception as e:
                    print(f'Error: {e}')
                    print(f'Line: {line}')
                    continue
    except FileNotFoundError:
        # create the file
        with open('amazon.json', 'w') as f:
            pass

    if id_only:
        try:
            return [set(item['orderID'] for item in return_list)]
        except:
            return []

    return return_list


def load_text_file(filename: str) -> str:
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def process_file(item):
    filename, text = item
    return parse_amazon_text(text, filename)

if __name__ == '__main__':
    GET_AMAZON_TRANSACTIONS = False
    if GET_AMAZON_TRANSACTIONS:
        headless = True
        login(headless=headless)
        old_trans_list = load_prior_results()
        new_trans_list = get_trans_list(headless=headless)

        # Remove any old transactions from the new list
        for trans in old_trans_list:
            if trans in new_trans_list:
                new_trans_list.remove(trans)

        pool = Pool(initializer=worker_init)

        # Map trans_list to parse_trans function across the pool
        pool.map(parse_trans, new_trans_list)

        pool.close()
        pool.join()
    else:
        directory_path = 'clean_soup'
        clean_soup_text = {}
        old_orders = load_prior_results(id_only=True)

        # Load files into dictionary
        for file in listdir(directory_path):
            order_id = file[:-4]
            new_order = order_id not in old_orders
            if file.endswith('.txt') and new_order:
                print(f'Loading file {file}')
                file_path = path.join(directory_path, file)
                clean_soup_text[order_id] = load_text_file(file_path)
            elif not file.endswith('.txt'):
                print(f'File {file} is not a .txt file')
            elif not new_order:
                print(f'Order {order_id} is already in the database')
            else:
                print(f'Unknown issue for file {file}')

        # Create a list of tuples for processing
        items_to_process = list(clean_soup_text.items())
        print(f'Got {len(items_to_process)} items to process')
        # Use multiprocessing to process files
        with Pool() as pool:
            print(f'Starting pool')
            results = pool.map(process_file, items_to_process)

        print(results)  # This will be a list of dictionary objects or None