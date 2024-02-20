from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pickle import dump, load
from time import sleep
from os import remove
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

def parse_amazon_text(text):
    thread = client.beta.threads.create()
    assistant = client.beta.assistants.retrieve(AMAZON_ASSISTANT_ID)

    run = client.beta.threads.runs.create(thread_id=thread.id,
                                          assistant_id=assistant.id,
                                          instructions=text + '\n' + amazon_user_prompt)

    run = wait_on_run(run, thread)

    run_results = loads(run.model_dump_json())
    result_dict = loads(run_results['required_action']['submit_tool_outputs']['tool_calls'][0]['function']['arguments'])

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
    parse_driver.set_window_size(225, total_height - (580 * 2))

    image_strings = []
    for page in range(1, 4):
        sleep(5)
        print(f'Parsing page {page}')
        # Save a screenshot
        parse_driver.execute_script("window.scrollTo(0, 0);")
        parse_driver.save_screenshot(f'page_{page}.png')
        print(f'Saved screenshot of page {page}')
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


def parse_trans(trans):
    if trans.startswith('D'):
        trans_url = f'https://www.amazon.com/gp/css/order-details?orderID={trans}'
        print(f'Skipping digital item {trans}')
        return
    else:
        trans_url = f'https://www.amazon.com/gp/css/summary/edit.html?orderID={trans}'

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
    if 'Something went wrong, please sign-in' not in clean_soup:
        parse_amazon_text(clean_soup)
    else:
        print('Something went wrong, please sign-in')

def load_prior_results():
    # {'orderID': '111-8079947-6269031', 'amount': 81.83, 'items': 'Computer Monitor'}
    # Iterate line by line. We need to returna a list of strings containing orderID only
    return_list = []
    with open('amazon.json', 'r') as f:
        for i, line in enumerate(f):
            # i used for debug counter
            try:
                return_list.append(eval(line)['orderID'])
            except Exception as e:
                print(f'Error: {e}')
                print(f'Line: {line}')
                continue

    return list(set(return_list))


if __name__ == '__main__':
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