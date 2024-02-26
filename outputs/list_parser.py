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

    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    title = ''
    description = ''
    labels = []
    return_vals = []
    for call in tool_calls:
        function_name = call.function.name
        for item in eval(call.function.arguments)['tasks']:
            title = item.get('title', 'No title')
            description = item.get('description', str(item))
            labels = item.get('labels', [])
            # switch case on function name
            match function_name:
                # shopping, chores, meals, school_work, unknown
                case "shopping":
                    return_vals.append(vikunja.add_shopping_item(title, labels, description))
                case "chores":
                    return_vals.append(vikunja.add_chore(title, labels, description))
                case "meals":
                    return_vals.append(vikunja.add_meal(title, labels, description))
                case "school_work":
                    return_vals.append(vikunja.add_school_work(title, labels, description))
                case "unknown":
                    return_vals.append(vikunja.add_unknown_item(title, labels, description))
    return f'Added {len(return_vals)} items to Vikunja'

if __name__ == '__main__':
    test_text = """
Image transcript: 
- Costco
  - Baby Wipes
  - Goldfish Bags
  - Quinoa Salad
  - TP (Toilet Paper)
  - Paper Towels
  - Beans
  - RAOS
  - AA, D, C Batt (Batteries)
  - Broccoli/Veggies
"""
    print(parse_list(test_text))
