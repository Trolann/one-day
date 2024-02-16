from multiprocessing import Process, Pipe
from dispatch.discord_bot import run_bot
from time import sleep
from settings import GENERAL_CHAN_ID

if __name__ == '__main__':
    # Setup a pipe for each task on the other side to consume
    p_systems, c_systems = Pipe()
    p_raw_msg, c_raw_msg = Pipe()

    # Start discord bot
    Process(target=run_bot, args=(c_systems, c_raw_msg,)).start()
    print("Waiting for bot to start")
    while not p_systems.poll():
        sleep(1) # Wait for bot to start
    print(p_systems.recv()[1]) # clear the systems pipe


    while True:
        message = input("Enter a message to send to Discord (m for messages, q to quit): ")
        if message == 'm':
            while p_raw_msg.poll():
                print(p_raw_msg.recv())
        elif message == 'q':
            break
        else:
            print(f"Sending message to Discord: {message}")
            p_raw_msg.send((GENERAL_CHAN_ID, message))


