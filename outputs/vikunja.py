from settings import VIKUNJA_API_KEY, VIKUNJA_API_URL
from requests import get, post, put, delete

class VikunjaAPI:
    def __init__(self):
        self.base_url = VIKUNJA_API_URL
        self.headers = {"Authorization": f"Bearer {VIKUNJA_API_KEY}"}

   # Projects
    def create_project(self, project_data):
        return put(f"{self.base_url}/projects", json=project_data, headers=self.headers).json()

    def get_all_projects(self):
        return get(f"{self.base_url}/projects", headers=self.headers).json()

    def get_project(self, project_id):
        return get(f"{self.base_url}/projects/{project_id}", headers=self.headers).json()

    def update_project(self, project_id, project_data):
        return post(f"{self.base_url}/projects/{project_id}", json=project_data, headers=self.headers).json()

    def delete_project(self, project_id):
        return delete(f"{self.base_url}/projects/{project_id}", headers=self.headers).json()

    # Tasks within a project
    def create_task(self, project_id, task_data):
        return put(f"{self.base_url}/projects/{project_id}/tasks", json=task_data, headers=self.headers).json()

    def get_tasks(self, project_id):
        return get(f"{self.base_url}/projects/{project_id}/tasks",
                   params={"sort_by": "due_date",
                           "order_by": "desc"},
                   headers=self.headers).json()

    def update_task(self, task_id, task_data):
        return post(f"{self.base_url}/tasks/{task_id}", json=task_data, headers=self.headers).json()

    def delete_task(self, task_id):
        return delete(f"{self.base_url}/tasks/{task_id}", headers=self.headers).json()


if __name__ == '__main__':
    vikunja = VikunjaAPI()

    from pprint import pprint
    #pprint(vikunja.get_all_projects())
    vikunja.create_task(1, {"title": "Test task 1", "description": "This is a test task"})
    from time import sleep
    tasks = vikunja.get_tasks(1)
    for task in tasks:
        #print(task)
        if task['title'] == "Apply for graduation":
            pprint(task['id'])
