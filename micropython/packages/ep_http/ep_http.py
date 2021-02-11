import socket
import re
import os
import json
import _thread
import time
import select
import ep_logging

class http_server:
    def __init__(self, micropython_optimize=False, routes=[], logger=None):
        self.micropython_optimize = micropython_optimize
        self.routes = routes
        self.logger = logger if logger is not None else ep_logging.default_logger(appname="http")

    def start(self):
        self.logger.info("Server started")
        s = socket.socket()
        ai = socket.getaddrinfo("0.0.0.0", 80)
        addr = ai[0][-1]
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(5)
        self.logger.debug("listening...")
        while True:
            r, w, err = select.select((s, ), (), (), 1)
            if r:
                for readable in r:
                    self.logger.debug("Waiting for new Connection")
                    client_sock, client_addr = s.accept()
                    self.logger.info("New client: " + str(client_addr))
                    
                    if not self.micropython_optimize:
                        client_stream = client_sock.makefile("rwb")
                    else:
                        client_stream = client_sock
                    try:
                        self.logger.debug("Reading Request")
                        req = client_stream.readline()
                        
                        self.logger.debug("Processing Request")
                        req = self.split_request(req)
                        if req is not None:
                            self.process_req(req, client_stream)
                    except Exception as e:
                        print('--- Caught Exception ---')
                        import sys
                        sys.print_exception(e)
                        self.logger.error("error")
                        print('----------------------------')
                    finally:
                        client_stream.close()
                        if not self.micropython_optimize:
                            client_sock.close()
                        self.logger.debug("Socked closed")


    def process_req(self, req, sock):
        req["header"] = header = self.split_header(sock)
        
        req["query"]  = ""
        if "?" in req["ressource"]:
            _, req["query"]  = req["ressource"].split("?")
        
        if req["method"] in ["POST", "PATCH", "PUT"]:
            req["query"] = sock.read(int(header["Content-Length"])).decode("utf8")
    
        req["fields"] = self.split_fields(req["query"], encoding=header.get("Content-Type", "application/x-www-form-urlencoded"))
        
        for route in self.routes:
            if re.match(route[0], req["ressource"]):
                req["route"] = route[0]
                self.logger.debug(req)
                route[1](sock, req)
                return
        else:
            self.logger.warning("no matching route found")

    def split_header(self, sock):
        header = {}
        while True:
            h = sock.readline().decode("utf8")
            if h == "" or h == "\r\n":
                break
            if ":" in h:
                key, val = h.split(": ")
                header[key] = val[:-2]
        return header


    def split_fields(self, query, encoding="application/x-www-form-urlencoded"):
        self.logger.debug("splitting fields, encoding is " + encoding)
        fields = {}
        if encoding == "application/x-www-form-urlencoded":
            if "=" in query:
                for field in query.split("&"):
                    key, val = field.split("=")
                    fields[key] = self.urlencode(val)
        elif encoding.startswith("text/plain"):
            fields = query
        elif encoding.startswith("application/json"):
            fields = json.loads(query)
        return fields


    def split_request(self, req):
        self.logger.debug("Splitting Request: " + str(req))
        g = re.match(r'(GET|POST|PUT|OPTIONS) (.*?) HTTP\/(.*)', req.decode("utf8"))
        if g is not None:
            request = {
                "method": g.group(1),
                "ressource": g.group(2)[1:],
                "version": g.group(3)[:-2]
            }
        else:
            request = None
            self.logger.warning("Invalid Request")
        
        return request               

    def urlencode(self, line):
        d = {
            r"+": " ",
            r"%20": "!", r"%21": "!", r"%22": '"', r"%23": "#", r"%24": "$", r"%25": "%", r"%26": "&", r"%27": "'",
            r"%28": "(", r"%29": ")", r"%2A": "*", r"%2B": "+", r"%2C": ",", r"%2D": "-", r"%2E": ".", r"%2F": "/",
            r"%3A": ":", r"%3B": ";", r"%3C": "<", r"%3D": "=", r"%3E": ">", r"%3F": "?",
            r"%4A": "@", r"%5B": "[", r"%5C": "\\", r"%5D": "]", r"%7B": "{", r"%7C": "|", r"%7D": "}",
        }
        for key in d:
            line = line.replace(key, d[key])
        return line



