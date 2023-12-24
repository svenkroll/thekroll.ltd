import logging
import os

from flask import Flask, Response, render_template, request

from services.stream_handler import stream_manager
from services.llm import LLMManager
from utils import create_vectordb, load_env_configuration

import config

app = Flask(__name__)
app.config.from_object(config)

logging.basicConfig(filename="app.log", level=logging.INFO, filemode="w")

load_env_configuration()
create_vectordb()
llm_manager = LLMManager(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form.get('prompt')

        stream_manager.prompt_queue.put(prompt)

        return {'status': 'success'}, 200

    css_version = int(os.stat('./app/static/css/app.css').st_mtime)
    return render_template('index.html', version=css_version)


@app.route('/stream', methods=['GET'])
def stream():
    def event_stream():
        return stream_manager.send_sse_data(llm_manager.qa_chain)

    return Response(event_stream(), content_type='text/event-stream')


app.run(debug=True, use_reloader=False)
