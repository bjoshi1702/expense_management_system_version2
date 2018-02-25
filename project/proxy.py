import socket
import json
import threading
import signal
import sys
import redis
from StringIO import StringIO
from httplib import HTTPResponse
from circuit_breaker import CircuitBreaker

r_server = redis.Redis("127.0.0.1")

MY_EXCEPTION = 'Threw Dependency Exception'
config =  {
            "HOST_NAME" : "0.0.0.0",
            "BIND_PORT" : 12345,
            "MAX_REQUEST_LEN" : 1024,
            "CONNECTION_TIMEOUT" : 10
          }


class Server:

    def __init__(self, config):
        signal.signal(signal.SIGINT, self.shutdown)
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((config['HOST_NAME'], config['BIND_PORT']))
        self.serverSocket.listen(10)
        self.__clients = {}
        self.k = 0


    def listenForClient(self):

        while True:
            (clientSocket, client_address) = self.serverSocket.accept()
            d = threading.Thread(name=self._getClientName(client_address), target=self.proxy_thread, args=(clientSocket, client_address))
            d.setDaemon(True)
            d.start()
        self.shutdown(0,0)


    def proxy_thread(self, conn, client_addr):

        request = conn.recv(config['MAX_REQUEST_LEN'])
        self.mainMethod(conn, request, 0)



    @CircuitBreaker(max_failure_to_open=3)
    def mainMethod(self, conn, request, port):
        try:

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = '127.0.0.1'
            port = int (port)
            s.connect((host, port))
            s.sendall(request)

            while True:
                data = s.recv(config['MAX_REQUEST_LEN'])
                if (len(data) > 0):
                    conn.send(data)
                else:
                    break
            s.close()
            conn.close()
            return 'DONE'

        except Exception as ex:
            print MY_EXCEPTION

    def _getClientName(self, cli_addr):
        return "Client"


    def shutdown(self, signum, frame):
        self.serverSocket.close()
        sys.exit(0)



if __name__ == "__main__":
    server = Server(config)
    server.listenForClient()
Blog  