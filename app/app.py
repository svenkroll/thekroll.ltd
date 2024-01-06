import os
from datetime import timedelta, datetime

from waitress import serve
from flask import Flask, Response, render_template, request

from services.stream_handler import StreamManager
from services.llm import LLMManager
from utils import load_env_configuration, configure_logging, validate_turnstile_token

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import config

TOKEN_EXPIRATION_TIME = timedelta(minutes=30)

app = Flask(__name__)
app.config.from_object(config)

validated_tokens = {}

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day"],
    storage_uri="memory://",
)

load_env_configuration()
configure_logging()
llm_manager = LLMManager(app)


def is_token_valid(token):
    if token in validated_tokens:
        token_time = validated_tokens[token]
        if datetime.now() - token_time < TOKEN_EXPIRATION_TIME:
            return True
    return False


def cleanup_expired_tokens():
    current_time = datetime.now()
    expired_tokens = [token for token, time in validated_tokens.items() if current_time - time > TOKEN_EXPIRATION_TIME]
    for token in expired_tokens:
        validated_tokens.pop(token)


@app.route('/', methods=['GET'])
@limiter.limit("10 per minute", error_message='Rate limit exceeded. Try again in a minute.')
def index():
    cleanup_expired_tokens()
    css_version = int(os.stat('./app/static/css/app.css').st_mtime)
    return render_template('index.html', version=css_version)


@app.get("/chat")
@limiter.limit("10 per minute", error_message='Rate limit exceeded. Try again in a minute.')
def chat_handler():
    prompt = request.args.get("message")
    token = request.args.get("token")

    if not is_token_valid(token):
        validation_result = validate_turnstile_token(token, os.getenv('TURNSTILE_SECRET'))
        if not validation_result.get('success'):
            return 'Token-Validierung fehlgeschlagen', 400
        validated_tokens[token] = datetime.now()

    stream_manager = StreamManager()

    # @stream_with_context
    def response_stream():
        return stream_manager.send_sse_data(prompt, llm_manager.qa_chain)

    return Response(response_stream(), mimetype="text/event-stream")


if __name__ == '__main__':
    threads = os.getenv("THREADS")
    environment = os.getenv("ENVIRONMENT")
    if environment == "production":
        serve(app, host='0.0.0.0', port="8080", threads=threads)
    else:
        app.run(debug=True, use_reloader=True)
