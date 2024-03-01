from settings import VIKUNJA_API_KEY, VIKUNJA_API_URL
from requests import get, post, put, delete
from datetime import datetime, timezone

class VikunjaAPI:
    def __init__(self):
        self.base_url = VIKUNJA_API_URL
        self.headers = {"Authorization": f"Bearer {VIKUNJA_API_KEY}"}
        self.SCHOOLWORK_LIST_ID = 31 #
        self.UNKNOWN_LIST_ID = 30
        self.MEALS_LIST_ID = 29 #
        self.CHORES_LIST_ID = 28 #
        self.SHOPPING_LIST_ID = 27 #
        self.COSTCO_LABEL_ID = 4
        self.GROCERIES_LABEL_ID = 5
        self.TARGET_LABEL_ID = 6
        self.AMAZON_LABEL_ID = 7
        self.HOMEWORK_LABEL_ID = 8
        self.ADMIN_LABEL_ID = 9
        self.PROJECT_LABEL_ID = 10
        self.EXAM_LABEL_ID = 11

    def add_unknown_item(self, title, labels = None, description=None, due_date=None):
        """
        Add an item to the unknown list
        """
        params = {"title": title}
        if description:
            if labels:
                try:
                    # Description with labels written on bottom
                    params['description'] = f"{description}\nLabels: {', '.join(labels)}"
                except TypeError:
                    # If labels is not a list
                    params['description'] = f"{description}\nLabels: {labels}"
            else:
                params['description'] = description
        if due_date:
            params['due_date'] = due_date

        return put(f"{self.base_url}/projects/{self.UNKNOWN_LIST_ID}/tasks",
                   json=params,
                   headers=self.headers).json()

    def add_chore(self, title, description=None, due_date=None):
        """
        Add an item to the chores list
        """
        params = {"title": title}
        if description:
            params['description'] = description
        if due_date:
            params['due_date'] = due_date

        return put(f"{self.base_url}/projects/{self.CHORES_LIST_ID}/tasks",
                   json=params,
                   headers=self.headers).json()

    def add_meal(self, title, description=None, due_date=None):
        """
        Add an item to the meals list
        """
        params = {"title": title}
        if description:
            params['description'] = description

        return put(f"{self.base_url}/projects/{self.MEALS_LIST_ID}/tasks",
                   json=params,
                   headers=self.headers).json()

    def add_school_work(self, title, labels: list, description=None, due_date=None):
        """
        Add an item to the schoolwork list
        """
        label_list = []
        params = {"title": title}

        # TODO: Labels aren't working right. They get sent here, but aren't being applied right.
        if 'homework' in labels:
            label_list.append(self.HOMEWORK_LABEL_ID)
        if 'admin' in labels:
            label_list.append(self.ADMIN_LABEL_ID)
        if 'project' in labels:
            label_list.append(self.PROJECT_LABEL_ID)
        if 'exam' in labels:
            label_list.append(self.EXAM_LABEL_ID)
        #if label_list:
        #    params['labels'] = label_list
        if description:
            params['description'] = description
        if due_date:
            try:
                # try and make iso time
                due_date = datetime.fromisoformat(due_date)
                params['due_date'] = due_date
            except ValueError:
                # Append whatever is the due date to the end of description
                params['description'] = f"{description}\nDue (unable to parse): {due_date}"

        response = put(f"{self.base_url}/projects/{self.SCHOOLWORK_LIST_ID}/tasks",
                   json=params,
                   headers=self.headers).json()

        for label_id in label_list:
            self.put_label(response['id'], label_id)

        return self.get_task(response['id'])

    def add_shopping_item(self, title, labels: list, description = None, due_date=None):
        """
        Add an item to the shopping list
        """
        label_list = []
        params = {"title": title}

        if 'amazon' in labels:
            label_list.append(self.AMAZON_LABEL_ID)
        if 'costco' in labels:
            label_list.append(self.COSTCO_LABEL_ID)
        if 'groceries' in labels:
            label_list.append(self.GROCERIES_LABEL_ID)
        if 'target' in labels:
            label_list.append(self.TARGET_LABEL_ID)

        #if label_list:
        #    params['labels'] = label_list


        if description:
            params['description'] = description
        if due_date:
            params['due_date'] = due_date

        response = put(f"{self.base_url}/projects/{self.SHOPPING_LIST_ID}/tasks",
                   json=params,
                   headers=self.headers).json()

        for label_id in label_list:
            self.put_label(response['id'], label_id)

        return self.get_task(response['id'])

    def get_tasks(self, project_id):
        return get(f"{self.base_url}/projects/{project_id}/tasks",
                   params={"sort_by": "due_date",
                           "order_by": "desc"},
                   headers=self.headers).json()

    def get_task(self, task_id):
        return get(f"{self.base_url}/tasks/{task_id}", headers=self.headers).json()

    def update_task(self, task_id, task_data):
        return post(f"{self.base_url}/tasks/{task_id}", json=task_data, headers=self.headers).json()

    def get_label(self, label_id):
        return get(f"{self.base_url}/labels/{label_id}", headers=self.headers).json()

    def put_label(self, task_id, label_id):
        data = {
            "label_id": label_id
        }
        return put(f"{self.base_url}/tasks/{task_id}/labels", json=data, headers=self.headers).json()


vikunja = VikunjaAPI()


if __name__ == '__main__':
    from pprint import pprint
    test_shopping_with_costco_label = {
        "title": "Test Shopping Item3",
        "labels": [],
        "label_id": [vikunja.COSTCO_LABEL['id']]
    }
    temp = test_shopping_with_costco_label
    test_shopping_with_costco_label['description'] = str(temp)

    print(vikunja.add_shopping_item(**test_shopping_with_costco_label))
    #print(vikunja.put_label(uid, vikunja.GROCERIES_LABEL['id']))
    pass
