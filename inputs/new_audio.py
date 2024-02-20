import requests
from subprocess import run
from random import choice
from string import ascii_lowercase


def download_and_convert(url: str):
    # Download the .ogg file
    response = requests.get(url)
    ogg_filename = 'downloaded_audio.ogg'
    with open(ogg_filename, 'wb') as audio_file:
        audio_file.write(response.content)
    # Convert .ogg to .mp4
    # Generate 10 random characters to use as a filename
    random_filename = ''.join(choice(ascii_lowercase) for i in range(10))
    run(['ffmpeg', '-i', ogg_filename, '-c:a', 'aac', '-strict', 'experimental', f'{random_filename}.mp4'])
    return f'{random_filename}.mp4'

