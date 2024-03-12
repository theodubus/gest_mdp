from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from security import *
import threading
from fonctions import *
import time

class AutoDeleteList(list):
    def __init__(self, delete_time=5):
        super().__init__()
        self.delete_time = delete_time

    def append(self, item):
        super().append(item)
        threading.Thread(target=self._delete_item, args=(item,), daemon=True).start()

    def _delete_item(self, item):
        time.sleep(self.delete_time)
        self.remove(item)

class RequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.domaines = dict()
        self.donnees = dict()
        self.mdp_maitre = ""
        self.login_links = list()
        self.last_requests = AutoDeleteList()

    def do_GET(self):

        # Vérification de l'adresse IP (localhost)
        host, port = self.client_address[:2]
        if host != '127.0.0.1':
            self.send_response(403)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Forbidden')
            return

        headers = self.headers

        if headers.get('data_type') != None:
            data_type = headers.get('data_type')

            # print(f"self.path: {self.path}")

            domains = list(self.domaines.keys())
            reponse = [domains, self.login_links]

            if data_type == "domains" and self.path == "/":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(reponse).encode())

            elif self.path[1:] in domains and data_type == "credentials":

                if self.path in self.last_requests:
                    self.send_response(429)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Too many requests')
                    return

                self.last_requests.append(self.path)

                compte = self.domaines[self.path[1:]]
                chaine_clair = decrypt(self.donnees[compte], self.mdp_maitre)
                l, login = link_login(chaine_clair)
                wait, prio, url = wait_prio_link(l)
                user, password = user_mdp(login)

                credentials = [user, password, wait]

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                # print(f"credentials: {credentials}")
                self.wfile.write(json.dumps(credentials).encode())
            elif self.path[1:] in domains and data_type == "double_auth":
                self.send_response(401)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'2FA has been removed as Authy discontinued its desktop app')
                return
            else:
                self.send_response(401)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Error data type')

        # Refus de la requête
        else:
            self.send_response(401)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Error data type')


class Server:
    def __init__(self, domaines, login_links, password, donnees, port=8000):
        self.port = port
        self.domaines = domaines
        self.password = password
        self.donnees = donnees
        self.server = None
        self.login_links = login_links

    def update_domaines(self, domaines, links):
        self.domaines = domaines
        self.login_links = links
        if self.server is not None:
            self.server.RequestHandlerClass.domaines = domaines
            self.server.RequestHandlerClass.login_links = links

    def update_password(self, password):
        self.password = password
        if self.server is not None:
            self.server.RequestHandlerClass.mdp_maitre = password

    def update_donnees(self, donnees):
        self.donnees = donnees
        if self.server is not None:
            self.server.RequestHandlerClass.donnees = donnees

    def is_stopped(self):
        return self.server is None

    def start_server(self):
        if self.server is None:
            self.server = HTTPServer(('localhost', self.port), RequestHandler)
            self.update_domaines(self.domaines, self.login_links)
            self.update_password(self.password)
            self.update_donnees(self.donnees)
            self.server.RequestHandlerClass.last_requests = AutoDeleteList()
            # print("starting server")
            self.server.server_activate()
            self.server.serve_forever()

    def stop_server(self):
        if self.server is not None:
            self.server.shutdown()
            # print("stopping server")
            self.server = None