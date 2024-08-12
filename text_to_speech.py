import os

import requests

voice_id = 'A2HjZWQYPQdztwZEK6hP'


def text_to_speech(text, file_id, credentails):
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": credentails["elevenlabs"]
    }

    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",  # This can handle cs language
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5,
            "use_speaker_boost": False,
            "style": 0.4,
        }
    }

    response = requests.post(url, json=data, headers=headers)
    file_name_temp = os.path.join("assets", "voices", file_id + "-temp.mp3")
    file_name_final = os.path.join("assets", "voices", file_id)

    with open(file_name_final, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    return file_id

    # With overlay
    # response = requests.post(url, json=data, headers=headers)
    # file_name_temp = os.path.join("assets", "voices", file_id + "-temp.mp3")
    # file_name_final = os.path.join("assets", "voices", file_id)
    #
    # with open(file_name_temp, 'wb') as f:
    #     for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
    #         if chunk:
    #             f.write(chunk)
    #
    # sound1 = AudioSegment.from_file(file_name_temp, format="mp3")
    # sound2 = AudioSegment.from_file(os.path.join("assets", "background", "water_quieter.mp3"), format="mp3")
    #
    # # Overlay sound2 over sound1 at position 0  (use louder instead of sound1 to use the louder version)
    # overlay = sound1.overlay(sound2, position=0, loop=True)
    #
    # # simple export
    # file_handle = overlay.export(file_name_final, format="mp3")
