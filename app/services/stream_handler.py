"""
This module provides the functionality to manage streaming data from a language model
to a client using Server-Sent Events (SSE). It includes classes to handle streaming
and process callbacks from the language model.
"""

import json
import threading
import time
from queue import Queue
from typing import Any, Dict, List

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult


class StreamManager:
    """
    Manages the streaming of data from a language model to a client.
    """
    def send_sse_data(self, prompt, qa_chain):
        """
        Streams data to a client using Server-Sent Events (SSE).
        """
        sse_event_queue = Queue()

        stream_handler = StreamHandler(sse_event_queue)
        response_thread = threading.Thread(target=qa_chain.run, args=(prompt,),
                                                kwargs={'callbacks': [stream_handler]})
        response_thread.start()

        try:
            while stream_handler.running:
                time.sleep(0.5)
                while not sse_event_queue.empty():
                    sse_event = sse_event_queue.get()
                    yield f"data: {json.dumps(sse_event)}\n\n"
        finally:
            stream_handler.running = False
            response_thread.join()  # Ensure the thread is terminated properly


class StreamHandler(BaseCallbackHandler):
    """
    Handles callbacks from a language model and queues them for streaming.
    """
    def __init__(self, sse_event_queue: Queue):
        self.sse_event_queue = sse_event_queue
        self.running = True

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.sse_event_queue.put({'type': 'token', 'content': token.replace('\n', '<br>')})

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        self.sse_event_queue.put({'type': 'start'})

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        self.sse_event_queue.put({'type': 'end'})
        self.running = False  # Stop the stream after the response is fully sent

    def on_llm_error(self, error: BaseException, **kwargs) -> None:
        self.sse_event_queue.put({'type': 'error', 'content': str(error)})
        self.running = False  # Stop the stream in case of an error
