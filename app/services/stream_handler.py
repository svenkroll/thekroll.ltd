import json
import threading
import time
from queue import Queue
from typing import Any, Dict, List

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult


class StreamManager:
    def send_sse_data(self, prompt, qa_chain):
        sse_event_queue = Queue()

        stream_handler = StreamHandler(sse_event_queue)
        response_thread = threading.Thread(target=qa_chain.run, args=(prompt,),
                                                kwargs={'callbacks': [stream_handler]})
        response_thread.start()

        while stream_handler.running:
            time.sleep(0.5)
            while not sse_event_queue.empty():
                sse_event = sse_event_queue.get()
                yield f"data: {json.dumps(sse_event)}\n\n"


class StreamHandler(BaseCallbackHandler):
    def __init__(self, sse_event_queue: Queue):
        self.sse_event_queue = sse_event_queue
        self.running = True

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.sse_event_queue.put({'type': 'token', 'content': token.replace('\n', '<br>')})

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        self.sse_event_queue.put({'type': 'start'})

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        self.sse_event_queue.put({'type': 'end'})

    def on_llm_error(self, error: BaseException, **kwargs) -> None:
        self.sse_event_queue.put({'type': 'error', 'content': str(error)})
