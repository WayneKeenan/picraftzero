#!/usr/bin/env python

from picraftzero.log import logger
import sys
import io
import os
import shutil
from subprocess import Popen, PIPE
from string import Template
from struct import Struct
from threading import Thread
from time import sleep, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from wsgiref.simple_server import make_server

import picamera
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIHandler, WSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

###########################################
# CONFIGURATION
WIDTH = 640
HEIGHT = 480
FRAMERATE = 24
HTTP_PORT = 8082
WS_PORT = 8084
COLOR = u'#444'
BGCOLOR = u'#333'
JSMPEG_MAGIC = b'jsmp'
JSMPEG_HEADER = Struct('>4sHH')
###########################################


class StreamingHttpHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
            return
        elif self.path == '/jsmpg.js':
            content_type = 'application/javascript'
            content = self.server.jsmpg_content
        elif self.path == '/index.html':
            content_type = 'text/html; charset=utf-8'
            tpl = Template(self.server.index_template)
            content = tpl.safe_substitute(dict(
                ADDRESS='%s:%d' % ("' + window.location.hostname +'", WS_PORT),
                WIDTH=WIDTH, HEIGHT=HEIGHT, COLOR=COLOR, BGCOLOR=BGCOLOR))
        else:
            self.send_error(404, 'File not found')
            return
        content = content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(content))
        self.send_header('Last-Modified', self.date_time_string(time()))
        self.end_headers()
        if self.command == 'GET':
            self.wfile.write(content)


class StreamingHttpServer(HTTPServer):
    def __init__(self):
        super(StreamingHttpServer, self).__init__(
                ('', HTTP_PORT), StreamingHttpHandler)
        with io.open('index.html', 'r') as f:
            self.index_template = f.read()
        with io.open('jsmpg.js', 'r') as f:
            self.jsmpg_content = f.read()


class StreamingWebSocket(WebSocket):
    def opened(self):
        self.send(JSMPEG_HEADER.pack(JSMPEG_MAGIC, WIDTH, HEIGHT), binary=True)


class BroadcastOutput(object):
    def __init__(self, camera):
        logger.debug('Spawning background conversion process')
        self.converter = Popen([
            'avconv',
            '-f', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-s', '%dx%d' % camera.resolution,
            '-r', str(float(camera.framerate)),
            '-i', '-',
            '-f', 'mpeg1video',
            '-b', '800k',
            '-r', str(float(camera.framerate)),
            '-'],
            stdin=PIPE, stdout=PIPE, stderr=io.open(os.devnull, 'wb'),
            shell=False, close_fds=True)

    def write(self, b):
        self.converter.stdin.write(b)

    def flush(self):
        logger.debug('Waiting for background conversion process to exit')
        self.converter.stdin.close()
        self.converter.wait()


class BroadcastThread(Thread):
    def __init__(self, converter, websocket_server):
        super(BroadcastThread, self).__init__()
        self.converter = converter
        self.websocket_server = websocket_server

    def run(self):
        try:
            while True:
                buf = self.converter.stdout.read(512)
                if buf:
                    self.websocket_server.manager.broadcast(buf, binary=True)
                elif self.converter.poll() is not None:
                    break
        finally:
            self.converter.stdout.close()

# Use this to set 'http_version' to 1.1
# Replacement for WebSocketWSGIRequestHandler class found in ws4py's wsgirefserver.py
class HTTP11WebSocketWSGIRequestHandler(WSGIRequestHandler):
    def handle(self):
        """
        Unfortunately the base class forces us
        to override the whole method to actually provide our wsgi handler.
        """
        self.raw_requestline = self.rfile.readline()
        if not self.parse_request(): # An error code has been sent, just exit
            return

        # next line is where we'd have expect a configuration key somehow
        handler = WebSocketWSGIHandler(
            self.rfile, self.wfile, self.get_stderr(), self.get_environ()
        )
        handler.request_handler = self      # backpointer for logging
        handler.http_version="1.1"          # This is the only addition to the original class that this replaces
        handler.run(self.server.get_app())

from picraftzero.config import get_config

def main():
    logger.info('Initializing camera')
    with picamera.PiCamera() as camera:
        config = get_config()
        w = config.getint('camera', 'width', fallback=640)
        h = config.getint('camera', 'height', fallback=480)
        camera.resolution = (w, h)
        camera.framerate = config.getint('camera', 'framerate', fallback=24)
        camera.rotation = config.getint('camera', 'rotation', fallback=0)
        camera.hflip = config.getboolean('camera', 'hflip', fallback=False)
        camera.vflip = config.getboolean('camera', 'vflip', fallback=False)
        camera.led = config.getboolean('camera', 'led', fallback=False)
        sleep(1) # camera warm-up tim
        logger.info('Initializing websockets server on port %d' % WS_PORT)
        websocket_server = make_server(
            '', WS_PORT,
            server_class=WSGIServer,
            handler_class=HTTP11WebSocketWSGIRequestHandler,
            app=WebSocketWSGIApplication(handler_cls=StreamingWebSocket))
        websocket_server.initialize_websockets_manager()
        websocket_thread = Thread(target=websocket_server.serve_forever)
        #logger.info('Initializing HTTP server on port %d' % HTTP_PORT)
        #http_server = StreamingHttpServer()
        #http_thread = Thread(target=http_server.serve_forever)
        logger.debug('Initializing broadcast thread')
        output = BroadcastOutput(camera)
        broadcast_thread = BroadcastThread(output.converter, websocket_server)
        logger.info('Starting recording')
        camera.start_recording(output, 'yuv')
        try:
            logger.debug('Starting websockets thread')
            websocket_thread.start()
            #logger.info('Starting HTTP server thread')
            #http_thread.start()
            logger.debug('Starting broadcast thread')
            broadcast_thread.start()
            while True:
                camera.wait_recording(1)
        except KeyboardInterrupt:
            pass
        finally:
            logger.info('Stopping recording')
            camera.stop_recording()
            logger.debug('Waiting for broadcast thread to finish')
            broadcast_thread.join()
            logger.debug('Shutting down HTTP server')
            #http_server.shutdown()
            logger.debug('Shutting down websockets server')
            websocket_server.shutdown()
            logger.debug('Waiting for HTTP server thread to finish')
            #http_thread.join()
            logger.debug('Waiting for websockets thread to finish')
            websocket_thread.join()


if __name__ == '__main__':
    main()
