from http.server import SimpleHTTPRequestHandler
import http.server
import json
import os
import socketserver
import threading

import psutil


HTTPSERVERPORT = 8081
if "SERVER_PORT" in os.environ:
    HTTPSERVERPORT = int(os.environ['SERVER_PORT'])

HTTPSERVERIP = '0'
if "SERVER_IP" in os.environ:
    HTTPSERVERIP = os.environ['SERVER_IP']


# Expose the REST API on port 8000
class BotAPI (SimpleHTTPRequestHandler ):

    def tail_file(self, filename, nline=10):
        with open(filename) as f:

            content = f.read().splitlines()
            offset = len(content) - nline
            if offset < 0:
                offset = 0

            return "".join(content[offset:])

    def checkbot(self):

        procs = [proc for proc in psutil.process_iter() \
            if 'python' in proc.name()]

        bots = [bot for bot in procs if  'bot' in bot.cmdline()[1]]
        if len(bots) < 1:
            print("bot has gone!")
            return False

        print("bot is stilling running!")
        return True

    def do_GET(self):
        if 'logs/' in self.path:
            # check logs
            log_file = os.path.join('..', 'Bot-scripts', 'bot.log')
            logs = self.tail_file(log_file)
            self.response_http(200, dict(data=logs))
            return

        # check status
        res = self.checkbot()
        self.response_http(200, dict(data=res))

    def  response_http(self, status, data=None):

        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        if data is not None:

            json_str = json.dumps(data)
            byte_str = bytes(json_str, 'UTF-8')
            self.wfile.write(byte_str)



class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """ server class """
    allow_reuse_address = True



class WebService(threading.Thread):
    """ server thread """

    WEBSERVER_NAME = 'BOT-API'

    def __init__(self):

        self._server = ThreadedHTTPServer((HTTPSERVERIP, HTTPSERVERPORT), BotAPI)
        super(WebService, self).__init__(target=self._server.serve_forever,
                                         name=self.WEBSERVER_NAME)
        ##self._event = threading.Event
        print("Server started on %s:%d" % (HTTPSERVERIP, HTTPSERVERPORT, ))

    def stop(self):
        """ stop thread """
        #self._stop = True
        self._server.shutdown()
        self._tstate_lock = None
        self._stop()



def main():
    """ main funcion """

    webserver = WebService()
    webserver.start()
    print("started....")

if __name__ == "__main__":
    main()
