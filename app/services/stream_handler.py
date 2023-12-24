import json
import threading
import time
from queue import Queue
from typing import Any, Dict, List

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult


class StreamManager:
    def __init__(self):
        self.prompt_queue = Queue()
        self.sse_event_queue = Queue()
        self.response_thread = None

    def send_sse_data(self, qa_chain):
        while True:
            if not self.prompt_queue.empty():
                if self.response_thread and self.response_thread.is_alive():
                    continue

                prompt = self.prompt_queue.get()
                stream_handler = StreamHandler(self.sse_event_queue)
                self.response_thread = threading.Thread(target=qa_chain.run, args=(prompt,),
                                                   kwargs={'callbacks': [stream_handler]})
                self.response_thread.start()

            while not self.sse_event_queue.empty():
                sse_event = self.sse_event_queue.get()
                yield f"data: {json.dumps(sse_event)}\n\n"

            time.sleep(1)


stream_manager = StreamManager()


class StreamHandler(BaseCallbackHandler):
    def __init__(self, sse_event_queue: Queue):
        self.sse_event_queue = sse_event_queue

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.sse_event_queue.put({'type': 'token', 'content': token.replace('\n', '<br>')})

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        self.sse_event_queue.put({'type': 'start'})

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        self.sse_event_queue.put({'type': 'end'})

    def on_llm_error(self, error: BaseException, **kwargs) -> None:
        self.sse_event_queue.put({'type': 'error', 'content': str(error)})