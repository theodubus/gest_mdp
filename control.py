import socket
import socketserver
from queue import Queue
from threading import Thread
from gest import *


class QueueHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.server = server
        server.client_address = client_address
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def handle(self):
        data = self.request.recv(4096)
        self.server.recv_q.put(data)
        self.request.send(data)


class TCPServer(socketserver.TCPServer):
    def __init__(self, ip, port, handler_class=QueueHandler):
        socketserver.TCPServer.__init__(self, (ip, port), handler_class, bind_and_activate=False)
        self.recv_q = Queue()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_bind()
        self.server_activate()

    def shutdown(self):
        socketserver.TCPServer.shutdown(self)

    def __del__(self):
        self.server_close()


class GestionnaireApplication(object):
    """
    Classe qui permet de gérer l'application :
    L'application est un des attributs de la classe GestionnaireApplication
    lorsqu'on ferme l'application, ce code continue de tourner et attend un message
    pour relancer l'application
    """
    def __init__(self):
        self.app = None
        self.launch_app_first()
        if not self.app.mdp_maitre or not get_master_password(self.app.mdp_user) or self.app.deconnexion:
            exit()

        self.server = TCPServer("localhost", 9999)

        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.start()
        self.stop = False

    def launch_app_first(self):
        self.app = Application()
        self.app.first_run()

    def relaunch_app(self):
        if self.app.menu is None:
            self.app.run()

    def run(self):
        while not self.server.recv_q.empty() and self.server.recv_q.queue[0].decode() == "lancer":
            self.server.recv_q.get()
        while not self.stop:

            # print("Waiting for data...")

            while not self.server.recv_q.empty():

                msg = self.server.recv_q.get()

                if msg.decode() == "lancer":
                    self.relaunch_app()
                    while not self.server.recv_q.empty() and self.server.recv_q.queue[0].decode() == "lancer":
                        self.server.recv_q.get()

                elif msg.decode() == "shutdown":
                    self.server.recv_q.queue.clear()
                    self.server.shutdown()
                    self.stop = True

            time.sleep(2)


if __name__ == "__main__":
    x = GestionnaireApplication()
    x.run()
