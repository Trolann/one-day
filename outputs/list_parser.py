#list_parser.py
from anthropic import Client
from outputs.vikunja import vikunja
from outputs.list_tools import list_tools
from datetime import datetime
from settings import OPUS, SONNET, HAIKU

client = Client()

def parse_list(text):
    messages = [{"role": "user", "content": f"Today's date is: {datetime.now().isoformat()}\nRequest:\n{text}"}]
    print('Calling Claude')
    response = client.beta.tools.messages.create(
        model=SONNET,
        max_tokens=4096,
        tools=list_tools,
        messages=messages
    )

    retries_left = 3 if response.stop_reason != "tool_use" else 0
    while retries_left:
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": "This is incorrect, respond with a tool call. "
                                                    "Please provide a tool call"})
        retries_left -= 1
        response = client.beta.tools.messages.create(
            model=SONNET,
            max_tokens=4096,
            tools=list_tools,
            messages=[
                {"role": "system", "content": "Please provide a tool call"}
            ]
        )

    return_vals = []
    for tool_call in [block for block in response.content if block.type == "tool_use"]:
        #tool_call = next(block for block in response.content if block.type == "tool_use")
        function_name = tool_call.name
        item = tool_call.input
        if type(tool_call.input) is not dict:
            try:
                item = eval(str(tool_call.input))
            except Exception as e:
                print(f'Error: {e}')
                print(f'Line: {tool_call.input}')
                continue
        title = item.get('title', 'No title')
        description = item.get('description', str(item))
        labels = item.get('labels', [])
        match function_name:
            case "shopping":
                return_vals.append(vikunja.add_shopping_item(title, labels, description))
            case "chores":
                return_vals.append(vikunja.add_chore(title, labels, description))
                # put label id 5 on the task
                vikunja.put_label(return_vals[-1]['id'], vikunja.LABELS['CHORES'])
            case "meals":
                return_vals.append(vikunja.add_meal(title, labels, description))
            case "school_work":
                return_vals.append(vikunja.add_school_work(title, labels, description))
            case "unknown":
                return_vals.append(vikunja.add_unknown_item(title, labels, description))

    return f'Added {len(return_vals)} items to Vikunja'

if __name__ == '__main__':
    print('Starting')
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
