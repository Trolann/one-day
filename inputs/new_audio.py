from requests import get
from subprocess import run
from random import choice
from string import ascii_lowercase
from os import remove
from os import devnull as dn
from openai import OpenAI
from settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_transcript(filename):
    with open(filename, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model='whisper-1',
            language='en',
            file=audio_file,
            prompt='If this sounds like a child, ignore it and response with \'I am a child\'',
            response_format='text'
        )
        remove(filename)
        return transcript

def download_and_convert(url: str):
    # Download the .ogg file
    response = get(url)
    ogg_filename = 'downloaded_audio.ogg'
    with open(ogg_filename, 'wb') as audio_file:
        audio_file.write(response.content)
    # Convert .ogg to .mp4
    # Generate 10 random characters to use as a filename
    random_filename = ''.join(choice(ascii_lowercase) for i in range(10))
    command = ['ffmpeg', '-i', ogg_filename, '-c:a', 'aac', '-strict', 'experimental', f'{random_filename}.mp4']

    # Redirect standard output and standard error to /dev/null
    with open(dn, 'wb') as devnull:
        run(command, stdout=devnull, stderr=devnull)
    remove(ogg_filename)
    return f'{random_filename}.mp4'

if __name__ == '__main__':
    url = 'https://cdn.discordapp.com/attachments/1205754903310630985/1209719186918477876/voice-message.ogg?ex=65e7f1c9&is=65d57cc9&hm=a422e217578f864362daf7a9030beab851a6bc3fc325a11e48d36d59c7d744eb&'
    filename = download_and_convert(url)
    print(get_transcript(filename))