from time import sleep
from openai import OpenAI
from json import loads
from settings import LIST_PARSER_ASSISTANT_ID, OPENAI_API_KEY
from outputs.vikunja import vikunja

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

def parse_list(text):
    thread = client.beta.threads.create()
    assistant = client.beta.assistants.retrieve(LIST_PARSER_ASSISTANT_ID)

    run = client.beta.threads.runs.create(thread_id=thread.id,
                                          assistant_id=assistant.id,
                                          instructions=text)

    run = wait_on_run(run, thread)

    run_results = loads(run.model_dump_json())

    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    labels = []
    for list in tool_calls:
        function_name = list['function']
        try:
            title = list.arguments['title']
        except:
            title = 'Error'
        try:
            description = list.arguments['description']
        except:
            description = str(list)
        try:
            labels = list.arguments['labels']
        except:
            pass
        # switch case on function name
        match function_name:
            # shopping, chores, meals, school_work, unknown
            case "shopping":
                return vikunja.add_shopping_item(title, labels, description)
            case "chores":
                return vikunja.add_chore(title, labels, description)
            case "meals":
                return vikunja.add_meal(title, labels, description)
            case "school_work":
                return vikunja.add_school_work(title, labels, description)
            case "unknown":
                return vikunja.add_unknown(title, labels, description)
