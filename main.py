import re
import os
import socket
import webbrowser
import threading
import uvicorn
import gradio as gr

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from Fsg_pp import demo

####### VARIABLES ########
BACKGROUND = "loading_screen.webp"
HOST = "127.0.0.1"   # Must match the host in the Gradio app
PORT = 7860          # Must match the port in the Gradio app


class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Process the request in a worker thread
        response = await call_next(request)
        path = request.url.path

        if path == "/":
            new_body = []
            head_re = re.compile("</head>")
            async for chunk in response.body_iterator:
                if "</head>" in chunk.decode():
                    chunk = head_re.sub(some_javascript + some_css + "</head>", chunk.decode()).encode()
                new_body.append(chunk)

            async def new_body_iterator(new_body):
                for chunk in new_body:
                    yield chunk

            response.body_iterator = new_body_iterator(new_body)

            # Update the Content-Length header
            response.headers["content-length"] = str(sum(len(chunk) for chunk in new_body))

        return response


def open_browser():
    url = "http://" + HOST + ":" + str(PORT)
    webbrowser.open(url)


def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


app = FastAPI(middleware=[Middleware(CustomMiddleware)])
app.mount("/bg", StaticFiles(directory="bg"), name="bg")

some_javascript = """
<script type="text/javascript">
window.onload = function() {
    var observer = new MutationObserver(function(mutations) {
        var pixivTab = document.querySelector('#pixiv_tab-button');

        if (pixivTab) {
            pixivTab.click();
            observer.disconnect();  // Stop observing once the actions are performed
        }
    });

    observer.observe(document, { childList: true, subtree: true });  // Start observing
};
</script>
"""

some_css = f"""
<style>
.svelte-15lo0d8.stretch > :nth-child(2) > div > div.svelte-1occ011 > .margin:after,
.svelte-15lo0d8.stretch > :nth-child(2) > div > div > div.svelte-1occ011 > .margin:after {{
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 130px;
  height: 130px;
  background-image: url('/bg/{BACKGROUND}');
  background-size: contain;
  background-repeat: no-repeat;
}}
</style>
"""

gr.mount_gradio_app(app, demo, path="/", app_kwargs={"max_request_size": 50000000, "timeout": 600})

# Check for environment variables
open_in_browser = os.environ.get('OPEN_IN_BROWSER') == '-o'
suppress_logs = os.environ.get('SUPPRESS_LOGS') == '-s'

if __name__ == "__main__":
    if open_in_browser:
        threading.Timer(1, open_browser).start()
    log_level = 'warning' if suppress_logs else 'info'
    
    port = PORT
    while check_port(HOST, port):
        print(f"Port {port} is already in use. Trying with port {port + 1}.")
        port += 1  # Increment the port number

    uvicorn.run("main:app", host=HOST, port=port, timeout_keep_alive=5000, ws_ping_interval=10, ws_ping_timeout=120, log_level=log_level)