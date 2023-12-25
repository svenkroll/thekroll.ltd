import logging
import os

from flask import Flask, Response, render_template, request

from services.stream_handler import StreamManager
from services.llm import LLMManager
from utils import create_vectordb, load_env_configuration

import config

app = Flask(__name__)
app.config.from_object(config)

logging.basicConfig(filename="app.log", level=logging.INFO, filemode="w")

load_env_configuration()
create_vectordb()
llm_manager = LLMManager(app)


@app.route('/', methods=['GET'])
def index():
    css_version = int(os.stat('./app/static/css/app.css').st_mtime)
    return render_template('index.html', version=css_version)


@app.get("/chat")
def chat_handler():
    prompt = request.args.get("message")
    stream_manager = StreamManager()

    # @stream_with_context
    def response_stream():
        return stream_manager.send_sse_data(prompt, llm_manager.qa_chain)

    return Response(response_stream(), mimetype="text/event-stream")


if __name__ == '__main__':
    app.run()
    #  app.run(debug=True, use_reloader=False)
