from picraftzero.log import logger
import os.path
import threading

# Pytohn 2 / 3 HTTP and Socket compatibility
try:
    from SimpleHTTPServer import SimpleHTTPRequestHandler # Python 2
except ImportError:
    from http.server import SimpleHTTPRequestHandler # Python 3

try:
    from SocketServer import TCPServer # Pytohn 2
except ImportError:
    from socketserver import TCPServer # Python 3

from picraftzero.thirdparty.SimpleWebSocketServer import SimpleWebSocketServer
from picraftzero.config import get_json_config, get_config




config = get_config()
logger.info("Config: {}".format(config))

class CustomRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/config.json':
            config_json = get_json_config()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", len(config_json))
            self.end_headers()
            self.wfile.write(bytes(config_json, 'utf-8'))
        else:
            return SimpleHTTPRequestHandler.do_GET(self)



class HTTPServer:


    def __init__(self, http_port = None):
        self.http_thread = None
        self.http_port = http_port if http_port else config['www']['http_port']
        TCPServer.allow_reuse_address = True
        self.httpd = None

    def _start(self):
        try:
            logger.info("Starting HTTP server on port {}".format(self.http_port))
            self.httpd = TCPServer(("", self.http_port), CustomRequestHandler)
            self.httpd.serve_forever()
        except Exception as e:
            logger.exception(e)

    def stop(self):
        logger.info("Stopping HTTP server")
        #self.httpd.server_close()
        if self.httpd:
            self.httpd.shutdown()

    def start(self):
        resource_path = os.path.join(os.path.split(__file__)[0], "resources")
        www_dir = resource_path + "/www"
        os.chdir(www_dir)
        logger.info("WWW dir: {}".format(www_dir))
        self.http_thread = threading.Thread(target=self._start, name = 'HTTPServer')
        self.http_thread.daemon = False # allow clean shutdown
        self.http_thread.start()


from picraftzero.thirdparty.SimpleWebSocketServer import WebSocket
import json

class DefaultWebSocketHandler(WebSocket):

    callee = None
    clients = []

    def handleConnected(self):
        logger.debug('handleConnected, from {}'.format(self.address))
        DefaultWebSocketHandler.clients.append(self)

    def handleClose(self):
        logger.debug('handleClose, from {}'.format(self.address))
        DefaultWebSocketHandler.clients.remove(self)


    def handleMessage(self):
        logger.debug('handleMessage, from {}'.format(self.address))
        try:
            obj = json.loads(self.data)
            DefaultWebSocketHandler.callee.on_websocket_message(obj)

        except Exception as e:
            logging.exception("Error in handleMessage")

    @staticmethod
    def send_all_clients_message(message):
        logger.debug("Sending all WS Clients: {}".format(message))
        for client in DefaultWebSocketHandler.clients:
            client.sendMessage(message)


class WebSocketServer:


    def __init__(self, callee, ws_port = None, ws_class=DefaultWebSocketHandler, ):
        self.ws_thread = None
        self.ws_port = ws_port if ws_port else config['www']['ws_port']
        self.ws = None
        self.ws_class = ws_class
        self.ws_class.callee = callee

    def _start(self):
        try:
            logger.info("Starting WebSocket server on port {}".format(self.ws_port))
            self.ws = SimpleWebSocketServer('', self.ws_port, self.ws_class)
            try:
                self.ws.serveforever()
                # eat errors as the server doesnt shutdown cleanly
                # erro would be: (file descriptor cannot be a negative integer (-1))
                # TODO: python2 still throws an exception on shutdown
            except ValueError:
                pass
        except Exception as e:
            logger.exception(e)

    def stop(self):
        logger.info("Stopping WebSocket server")
        if self.ws:
            self.ws.close()

    def start(self):
        self.ws_thread = threading.Thread(target=self._start, name = 'WebSocketServer')
        self.ws_thread.daemon = True
        self.ws_thread.start()


    def send_message(self, message):
        json_string = json.dumps(message)
        self.ws_class.send_all_clients_message(json_string)




from .thirdparty.pistreaming import server as pistreaming_server

class CameraServer:


    def __init__(self):
        self.camera_thread = None
        self.camera_server = None

    def _start(self):
        try:
            logger.info("Starting CameraServer server")
            pistreaming_server.main()
        except Exception as e:
            logger.exception(e)

    def stop(self):
        logger.info("Stopping Camera server")
        #if self.camera_server:
            #self.camera_server.shutdown()

    def start(self):
        self.camera_thread = threading.Thread(target=self._start, name = 'CameraServer')
        self.camera_thread.daemon = False # allow clean shutdown
        self.camera_thread.start()
