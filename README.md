# Project Glowfish (aka Innocent Old Lady)

## Prerequisites

- python 3 (3.11)
- ffmpeg
- packages from requirements.txt
- publicly available domain (for Twilio webhooks)
- Gemini API key, Twilio sid and token, ElevenLabs token

## Project structure

- main.py (main script responsible for Flask server definition and endpoint calls handling)
- assets (assets available via Flask server for use from Twilio)
- models.py (module containing the gemini models definitions and prompts)
- text_to_speach.py
- utils.py (general utility functions)
- calls.py (twilio functions)
- CallMetadata
- credentials.json (file containing the credentials for the project)

## Running the project

In order to run the "Innocent Old Lady" server, update your credentials file and start the main.py Python script

```
python main.py [--host {host=0.0.0.0}] [--port {port=3000}] [--credentials-file {file=credentials.json}] --base-url {url}
```

- host - the host on which the server will be running (default: 0.0.0.0)
- port - the port on which the server will be running (default: 3000)
- credentials-file - the path to the credentials file (default: credentials.json)
- base_url - base url of the server available from the internet (for twilio webhooks)

##
