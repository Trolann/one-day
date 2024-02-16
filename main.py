from multiprocessing import Process, Pipe
from dispatch.discord_bot import run_bot
from time import sleep
from settings import GENERAL_CHAN_ID
from inputs.new_image import process_image_requests

if __name__ == '__main__':
    # Setup a pipe for each task on the other side to consume
    p_systems, c_systems = Pipe()
    p_raw_msg, c_raw_msg = Pipe()
    p_images, c_images = Pipe()

    # Start discord bot
    Process(target=run_bot, args=(c_systems, c_raw_msg, c_images,)).start()
    print("Waiting for bot to start")
    while not p_systems.poll():
        sleep(1) # Wait for bot to start
    print(p_systems.recv()[1]) # clear the systems pipe


    while True:
        #message = input("Enter a message to send to Discord (q to quit): ")
        message = 'ping?'
        if p_images.poll():
            image_requests = []
            # Consume all messages from the pipe in id:content pairs
            while p_images.poll():
                image_requests.append(p_images.recv())
                request_dict = image_requests[-1]
                print(f"ID: {request_dict['message_id']}")
                print(f"Request: {request_dict}")
            responses = process_image_requests(image_requests)
            #print(f'Responses: {responses}')
            print(f"Resonses[0].choice[0].message.content: {responses[0].choices[0].message.content}")
            p_raw_msg.send((GENERAL_CHAN_ID, "```\n" + responses[0].choices[0].message.content + "\n```"))


        if p_raw_msg.poll():
            message = p_raw_msg.recv()
            print(f"Received message: {message}")


