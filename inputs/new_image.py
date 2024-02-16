from openai import OpenAI
from settings import OPENAI_API_KEY, image_sys_prompt, image_user_prompt

client = OpenAI(api_key=OPENAI_API_KEY)


def is_image(url):
    if 'https://' not in url:
        return False
    # Attempting a different approach to ensure correct filename extraction and extension checking
    try:
        # Extract the part of the URL after the last '/' and before any '?'
        filename = url.split('/')[-1].split('?')[0]
        # Define a list of known image extensions
        known_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
        # Check if the extracted filename ends with any of the known image extensions
        return any(filename.lower().endswith(ext) for ext in known_extensions)
    except Exception as e:
        # In case of any error, log it and return False
        print(f"Error: {e}")
        return False

def process_image_requests(image_requests: list):
    print(f"Processing {len(image_requests)} image requests")
    responses = []
    for request in image_requests:
        message = [
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": image_sys_prompt},
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": request["prompt"] + image_user_prompt
                    },
                ],
            }
        ]
        for image_url in request.get("images", []):
            if not image_url:
                continue
            message[1]["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    }
                }
            )
            print("Added image url to message")
        print(message)
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=message,
            max_tokens=300,
        )
        print('Got a gpt response!')
        responses.append(response)
    return responses
