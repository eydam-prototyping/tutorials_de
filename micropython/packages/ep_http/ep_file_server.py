import ep_default_server
import os
import re
import ep_logging

class file_server(ep_default_server.default_server):
    def __init__(self, html_dir, default_file="config.html", logger=None):
        super().__init__()
        self.html_dir = html_dir
        self.default_file = default_file
        self.logger = logger if logger is not None else ep_logging.default_logger(appname="http_fs")

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
        self.logger.debug("Requested file: " + file)
        if file in ["", "/"]:
            file = self.default_file
        if file == "favicon.ico":
            file = "favicon.png"
        self.logger.info("Served file: " + file)
        if file in os.listdir(self.html_dir):
            with open(self.html_dir + file, "rb") as f:
                data = f.read(512)
                while data != b"":
                    sock.send(data)
                    data = f.read(512)