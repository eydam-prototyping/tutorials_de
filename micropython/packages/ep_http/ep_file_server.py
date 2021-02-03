import ep_default_server
import os
import re

class file_server(ep_default_server.default_server):
    def __init__(self, html_dir, default_file="config.html"):
        super().__init__()
        self.html_dir = html_dir
        self.default_file = default_file

    def serve(self, sock, request):
        if "?" in request["ressource"]:
            file, _ = request["ressource"].split("?")
        else:
            file = request["ressource"]

        m = re.match(request["route"], file)
        sock.write(b"HTTP/1.1 200 OK\r\n")  

        header = {
            "Content-Type": "text/html; charset=UTF-8",
        }
        header["Connection"] = "close"
            
        self.send_header(sock, header)
        sock.write(b"\r\n")
        self.return_file(m.group(1), sock)

    def return_file(self, file, sock):
        if file == "":
            file = self.default_file
        if file == "favicon.ico":
            file = "favicon.png"
        #print(file)
        if file in os.listdir(self.html_dir):
            with open(self.html_dir + file, "rb") as f:
                sock.write(f.read())