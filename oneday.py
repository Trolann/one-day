from multiprocessing import Process, Pipe
from dispatch.discord_bot import run_bot
from time import sleep
from settings import GENERAL_CHAN_ID
from inputs.new_image import process_image_requests
from inputs.new_audio import download_and_convert, get_transcript
from outputs.list_parser import parse_list
from logging import getLogger, basicConfig, StreamHandler, DEBUG
from sys import stdout

if __name__ == "__main__":
    # Set up a pipe for each task on the other side to consume
    p_systems, c_systems = Pipe()
    p_raw_msg, c_raw_msg = Pipe()
    p_images, c_images = Pipe()
    p_audio, c_audio = Pipe()
    # Set up the logger
    print('starting')
    basicConfig(
        level=DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            StreamHandler(stdout)
        ]
    )

    # Start discord bot
    bot = Process(
        target=run_bot,
        args=(
            c_systems,
            c_raw_msg,
            c_images,
            c_audio,
        ),
    )
    bot.start()
    logger = getLogger(__name__)
    logger.setLevel('DEBUG')
    logger.info("Waiting for bot to start")
    while not p_systems.poll():
        sleep(1)  # Wait for bot to start
    logger.debug(p_systems.recv()[1])  # clear the systems pipe

    try:
        while True:
            sleep(0.1)
            # message = input("Enter a message to send to Discord (q to quit): ")
            message = "ping?"
            dispatch_request = ""
            if p_images.poll():
                request_dict = {}
                image_requests = []
                # Consume all messages from the pipe in id:content pairs
                while p_images.poll():
                    image_requests.append(p_images.recv())
                    request_dict = image_requests[-1]

                responses = process_image_requests(image_requests)
                # print(f'Responses: {responses}')
                transcript = responses[0].choices[0].message.content
                # p_raw_msg.send((GENERAL_CHAN_ID, "```\n" + transcript + "\n```"))
                # p_raw_msg.send((GENERAL_CHAN_ID, "```\n" + str(request_dict) + "\n```"))
                dispatch_request = (
                    request_dict["prompt"] + "\n Image transcript: \n" + transcript
                )
                p_raw_msg.send((GENERAL_CHAN_ID, "```\n" + dispatch_request + "\n```"))
            if p_raw_msg.poll():
                message = p_raw_msg.recv()
                logger.debug(f"Received message: {message}")

                dispatch_request = message[1]
            if p_audio.poll():
                message = p_audio.recv()
                audio_transcript = get_transcript(
                    download_and_convert(message["audio"][0])
                )
                print(f"Received audio request: \n{audio_transcript}")
                dispatch_request = (
                    "This is a transcript of an audio request: \n" + audio_transcript
                )
                p_raw_msg.send((GENERAL_CHAN_ID, "```\n" + dispatch_request + "\n```"))

            if dispatch_request:
                parsed_list = parse_list(dispatch_request)
                p_raw_msg.send((GENERAL_CHAN_ID, "```\n" + parsed_list + "\n```"))
    finally:
        bot.kill()
        bot.join()
        logger.error("Bot terminated")
