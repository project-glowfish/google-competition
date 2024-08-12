import argparse
import json
import threading
import time
import uuid

import google.generativeai as genai
from flask import Flask, request, make_response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from CallMetadata import CallMetadata
from calls import play_text, play_placeholder, listen
from models import analysis_model, response_model, query_chat
from text_to_speech import text_to_speech
from utils import log

app = Flask(__name__, static_folder='assets')
client: Client
calls = {}
credentials = {}
base_url = ""


def analyze_caller_input(user_input, chat, call_metadata: CallMetadata):
    analysis_response = query_chat(chat, user_input, call_metadata)
    return analysis_response


def generate_response(analysis, chat, call_metadata: CallMetadata):
    response = query_chat(chat, analysis, call_metadata)
    return response


@app.route('/health', methods=['GET'])
def test():
    return "It works!"


def ensure_models_created(call_metadata: CallMetadata):
    if call_metadata.chat_analytical is None:
        log("Creating chat models", call_metadata)
        call_metadata.context_analysis = []
        call_metadata.chat_analytical = analysis_model.start_chat(history=call_metadata.context_analysis)

        call_metadata.context_results = []
        call_metadata.chat_results = response_model.start_chat(history=call_metadata.context_results)
        log("Created", call_metadata)


@app.route('/partial', methods=['POST'])
def partial():
    partial_result = request.form.get('UnstableSpeechResult')
    call_id = request.form.get('CallSid')
    call_metadata = get_call_info(request.form)

    if len(partial_result) > 50 and (call_metadata.last_analysis_length is None or (
            len(partial_result) - call_metadata.last_analysis_length) > 30):
        thread = threading.Thread(target=analyse_partial,
                                  args=(call_metadata, partial_result))
        call_metadata.add_analysis(thread)
        thread.start()

    return "ok"


def analyse_partial(call_metadata: CallMetadata, partial_result):
    call_metadata.last_analysis_length = len(partial_result)

    ensure_models_created(call_metadata)

    start_time = time.time()
    analysis = analyze_caller_input(partial_result, call_metadata.chat_analytical, call_metadata)
    log(f"Partial analysis finished (took {time.time() - start_time:.2f} seconds)", call_metadata)
    call_metadata.last_analysis_info = analysis


def get_call_info(form) -> CallMetadata:
    caller = request.form.get('Caller')
    call_id = request.form.get('CallSid')

    if call_id not in calls:
        calls[call_id] = CallMetadata(call_id, caller)

    return calls[call_id]


def prepare_sound_and_listen(call_metadata: CallMetadata, speech_result, confidence):
    # Process the speech result with AI
    ensure_models_created(call_metadata)

    analysis = call_metadata.last_analysis_info if call_metadata.last_analysis_info is not None else "Analysis not found"
    call_metadata.reset_analysis()

    response_input = "I1: " + speech_result + " ||| I2: " + analysis
    start_time = time.time()
    response = generate_response(response_input, call_metadata.chat_results, call_metadata)
    log(f"Response finished (took {time.time() - start_time:.2f} seconds)", call_metadata)

    file_id = str(uuid.uuid4()) + '.mp3'
    start_time = time.time()
    mp3_file = text_to_speech(response, file_id, credentials)
    log(f"MP3 generation finished (took {time.time() - start_time:.2f} seconds)", call_metadata)

    start_time = time.time()
    log("MP3 eleven labs finished", call_metadata)
    call = client.calls(str(call_metadata.call_id)).update(
        twiml=f'<Response><Play>' + base_url + f'/assets/voices/{mp3_file}</Play><Gather input="speech" speech_timeout="auto" action="/voice" language="cs-CZ" partialResultCallback="' + base_url + '/partial"></Gather></Response>'
    )

    log(f"Call updated (took {time.time() - start_time:.2f} seconds)", call_metadata)


@app.route('/voice', methods=['POST'])
def voice():
    twiml = VoiceResponse()

    call_metadata = get_call_info(request.form)

    speech_result = request.form.get('SpeechResult')
    confidence = request.form.get('Confidence')

    log(f"Received voice request (call id: {call_metadata.call_id})", call_metadata)
    log(f'Recognized speach {speech_result} (confidence: {confidence})', call_metadata)

    if speech_result:
        try:
            play_placeholder(twiml, call_metadata, base_url)

            thread = threading.Thread(target=prepare_sound_and_listen,
                                      args=(call_metadata, speech_result, confidence))
            thread.start()
            listen(twiml, credentials, base_url)
        except Exception as error:
            print('Error processing request:', error)
            play_text('Omlouvám se, někdo mi volá, můžete mi zavolat prosím za chvíli?', twiml, credentials, base_url)
            twiml.redirect('/voice')
    else:
        print("No speech result")
        listen(twiml, credentials, base_url, "Haló? Kdo je tam?")

    response = make_response(str(twiml))
    response.headers['Content-Type'] = 'text/xml'
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False, type=str, default="0.0.0.0")
    parser.add_argument('--port', required=False, type=int, default=3000)
    parser.add_argument('--credentials_file', required=False, type=str, default="credentials.json")
    parser.add_argument('--base_url', required=True, type=str)

    parsed_args = vars(parser.parse_args())

    with open(parsed_args['credentials_file'], "r") as f:
        credentials = json.load(f)

    client = Client(username=credentials["twilio"]["sid"], password=credentials["twilio"]["token"], region="ie1",
                    edge="dublin")
    genai.configure(api_key=credentials["geminiapi"])

    base_url = parsed_args['base_url']

    app.run(host=parsed_args['host'], port=parsed_args['port'], debug=True)
