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
        self.COSTCO_LABEL = self.get_label(4)
        self.GROCERIES_LABEL = self.get_label(5)
        self.TARGET_LABEL = self.get_label(6)
        self.AMAZON_LABEL = self.get_label(7)
        self.HOMEWORK_LABEL = self.get_label(8)
        self.ADMIN_LABEL = self.get_label(9)
        self.PROJECT_LABEL = self.get_label(10)
        self.EXAM_LABEL = self.get_label(11)

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
            label_list.append(self.HOMEWORK_LABEL)
        if 'admin' in labels:
            label_list.append(self.ADMIN_LABEL)
        if 'project' in labels:
            label_list.append(self.PROJECT_LABEL)
        if 'exam' in labels:
            label_list.append(self.EXAM_LABEL)
        if label_list:
            params['labels'] = label_list
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


        return put(f"{self.base_url}/projects/{self.SCHOOLWORK_LIST_ID}/tasks",
                   json=params,
                   headers=self.headers).json()

    def add_shopping_item(self, title, labels: list, description = None, due_date=None):
        """
        Add an item to the shopping list
        """
        label_list = []
        params = {"title": title}

        if 'amazon' in labels:
            label_list.append(self.AMAZON_LABEL)
        if 'costco' in labels:
            label_list.append(self.COSTCO_LABEL)
        if 'groceries' in labels:
            label_list.append(self.GROCERIES_LABEL)
        if 'target' in labels:
            label_list.append(self.TARGET_LABEL)
        if label_list:
            params['labels'] = label_list
        if description:
            params['description'] = description
        if due_date:
            params['due_date'] = due_date


        return put(f"{self.base_url}/projects/{self.SHOPPING_LIST_ID}/tasks",
                   json=params,
                   headers=self.headers).json()

    def get_tasks(self, project_id):
        return get(f"{self.base_url}/projects/{project_id}/tasks",
                   params={"sort_by": "due_date",
                           "order_by": "desc"},
                   headers=self.headers).json()

    def update_task(self, task_id, task_data):
        return post(f"{self.base_url}/tasks/{task_id}", json=task_data, headers=self.headers).json()

    def get_label(self, label_id):
        return get(f"{self.base_url}/labels/{label_id}", headers=self.headers).json()


vikunja = VikunjaAPI()


if __name__ == '__main__':
    for label in (vikunja.COSTCO_LABEL, vikunja.GROCERIES_LABEL, vikunja.TARGET_LABEL, vikunja.AMAZON_LABEL, vikunja.HOMEWORK_LABEL, vikunja.ADMIN_LABEL, vikunja.PROJECT_LABEL, vikunja.EXAM_LABEL):
        print(label)