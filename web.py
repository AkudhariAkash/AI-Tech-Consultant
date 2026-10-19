"""Tiny dependency-free frontend server for the local dashboard."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
ROOT=os.path.dirname(os.path.abspath(__file__))
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=os.path.join(ROOT,"frontend"),**kwargs)
    def log_message(self,format,*args): pass
ThreadingHTTPServer(("127.0.0.1",8081),Handler).serve_forever()
