from settings import VIKUNJA_API_KEY, VIKUNJA_API_URL
from requests import get, post, put, delete
from requests.exceptions import ConnectionError, HTTPError
from datetime import datetime
from time import sleep

class VikunjaAPI:
    def __init__(self, max_retries=10, retry_delay=1):
        self.base_url = VIKUNJA_API_URL
        self.headers = {"Authorization": f"Bearer {VIKUNJA_API_KEY}"}
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.SCHOOLWORK_LIST_ID = 31
        self.UNKNOWN_LIST_ID = 30
        self.MEALS_LIST_ID = 29
        self.CHORES_LIST_ID = 28
        self.SHOPPING_LIST_ID = 27

        self.LABELS = {
            'COSTCO': 4,
            'GROCERIES': 5,
            'TARGET': 6,
            'AMAZON': 7,
            'HOMEWORK': 8,
            'ADMIN': 9,
            'PROJECT': 10,
            'EXAM': 11
        }

    def _make_request(self, method, url, **kwargs):
        for retry in range(self.max_retries):
            try:
                if True: # Set to False to disable debug output and actually call Vikunja
                    url = url[len(self.base_url):]
                    url_parts = url.split('/')
                    if url_parts[1] == 'projects':
                        try:
                            url_parts[2] = int(url_parts[2])
                        except:
                            pass
                        match url_parts[2]:
                            case self.UNKNOWN_LIST_ID:
                                url_parts[2] = 'unknown'
                            case self.CHORES_LIST_ID:
                                url_parts[2] = 'chores'
                            case self.MEALS_LIST_ID:
                                url_parts[2] = 'meals'
                            case self.SCHOOLWORK_LIST_ID:
                                url_parts[2] = 'school_work'
                            case self.SHOPPING_LIST_ID:
                                url_parts[2] = 'shopping'
                    url = '/'.join(url_parts)
                    print(f"Debug: {url}\n{kwargs['json'] if 'json' in kwargs else kwargs}")
                    return None
                response = method(url, **kwargs)
                response.raise_for_status()
                return response.json()
            except (ConnectionError, HTTPError) as e:
                if retry < self.max_retries - 1:
                    sleep(self.retry_delay)
                else:
                    raise e

    def add_unknown_item(self, title, labels=None, description=None, due_date=None):
        params = {"title": title}
        if description:
            if labels:
                params['description'] = f"{description}\nLabels: {', '.join(labels)}"
            else:
                params['description'] = description
        if due_date:
            params['due_date'] = due_date

        return self._make_request(put, f"{self.base_url}/projects/{self.UNKNOWN_LIST_ID}/tasks", json=params, headers=self.headers)

    def add_chore(self, title, description=None, due_date=None):
        params = {"title": title}
        if description:
            params['description'] = description
        if due_date:
            params['due_date'] = due_date

        return self._make_request(put, f"{self.base_url}/projects/{self.CHORES_LIST_ID}/tasks", json=params, headers=self.headers)

    def add_meal(self, title, description=None, due_date=None):
        params = {"title": title}
        if description:
            params['description'] = description

        return self._make_request(put, f"{self.base_url}/projects/{self.MEALS_LIST_ID}/tasks", json=params, headers=self.headers)

    def add_school_work(self, title, labels, description=None, due_date=None):
        label_ids = [self.LABELS[label.upper()] for label in labels if label.upper() in self.LABELS]
        params = {"title": title}

        if description:
            params['description'] = description
        if due_date:
            try:
                due_date = datetime.fromisoformat(due_date)
                params['due_date'] = due_date
            except ValueError:
                params['description'] = f"{description}\nDue (unable to parse): {due_date}"

        return self._handle_request(label_ids, params)

    def add_shopping_item(self, title, labels, description=None, due_date=None):
        label_ids = [self.LABELS[label.upper()] for label in labels if label.upper() in self.LABELS]
        params = {"title": title}

        if description:
            params['description'] = description
        if due_date:
            params['due_date'] = due_date

        return self._handle_request(label_ids, params)

    def _handle_request(self, label_ids, params):
        response = self._make_request(put, f"{self.base_url}/projects/{self.SHOPPING_LIST_ID}/tasks", json=params,
                                      headers=self.headers)
        for label_id in label_ids:
            try:
                self.put_label(response['id'], label_id)
            except TypeError as e:
                if response:
                    print(f"Error: {e}")
                    print(f"Label ID: {label_id}")
                    print(f"Response: {response}")
                # Convert label_id to string for debugging
                labels = []
                for label in self.LABELS:
                    if self.LABELS[label] == label_id:
                        labels.append(label)
                print(f'Labels: {labels}')
                continue
        return self.get_task(response['id']) if response else None

    def get_tasks(self, project_id):
        return self._make_request(get, f"{self.base_url}/projects/{project_id}/tasks",
                                  params={"sort_by": "due_date", "order_by": "desc"},
                                  headers=self.headers)

    def get_task(self, task_id):
        return self._make_request(get, f"{self.base_url}/tasks/{task_id}", headers=self.headers)

    def update_task(self, task_id, task_data):
        return self._make_request(post, f"{self.base_url}/tasks/{task_id}", json=task_data, headers=self.headers)

    def get_label(self, label_id):
        return self._make_request(get, f"{self.base_url}/labels/{label_id}", headers=self.headers)

    def put_label(self, task_id, label_id):
        data = {"label_id": label_id}
        return self._make_request(put, f"{self.base_url}/tasks/{task_id}/labels", json=data, headers=self.headers)


vikunja = VikunjaAPI()

if __name__ == '__main__':
    from pprint import pprint
    test_shopping_with_costco_label = {
        "title": "blah men",
        "labels": ["amazon", "target"]
    }
    temp = test_shopping_with_costco_label
    test_shopping_with_costco_label['description'] = str(temp)

    print(vikunja.add_shopping_item(**test_shopping_with_costco_label))
    #print(vikunja.put_label(uid, vikunja.GROCERIES_LABEL['id']))
    pass
