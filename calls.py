import json
import os
import uuid
import random

from twilio.twiml.voice_response import Play, Gather

from CallMetadata import CallMetadata
from text_to_speech import text_to_speech


def play_text(text, twiml, credentials, base_url):
    gather = Gather(input='speech', speech_timeout='auto', action='/voice', language="cs-CZ",
                    partialResultCallback="/partial")

    file_id = str(uuid.uuid4()) + '.mp3'
    mp3_file = text_to_speech(text, file_id, credentials)
    play = Play(base_url + "/assets/voices/" + mp3_file)

    gather.append(play)
    twiml.append(gather)


def play_placeholder(twiml, call_info: CallMetadata, base_url):
    print(call_info.last_analysis_info)
    last_analysis = json.loads(call_info.last_analysis_info) if call_info.last_analysis_info is not None else None
    # folder = last_analysis["file"] if last_analysis is not None else "background/thinking"
    folder = "background/thinking"

    # Path to the directory containing your audio files
    base_dir = "assets"
    folder_path = os.path.join(base_dir, "voice", folder)

    # List all files in the chosen folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Pick a random file from the folder
    chosen_file = random.choice(files)

    # Create the full path for the file to play
    file_to_play = os.path.join("voice", folder,
                                chosen_file) if last_analysis is not None else "background/thinking.mp3"
    print("Chosen file:", file_to_play)

    # Append the Play command with the chosen file to the TwiML response
    play = Play(base_url + f"/assets/{file_to_play}")
    twiml.append(play)
    return file_to_play


def listen(twiml, credentials, base_url, text=""):
    if text != "":
        play_text(text, twiml, credentials, base_url)
    else:
        gather = Gather(input='speech', speech_timeout='auto', action='/voice', language="cs-CZ",
                        partialResultCallback="/partial")
        # gather.say(text, voice='Google.cs-CZ-Standard-A', language="cs-CZ")
        twiml.append(gather)
