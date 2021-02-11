import ep_default_server
import re
import json
import ep_config
import ep_logging

class rest_server(ep_default_server.default_server):
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger if logger is not None else ep_logging.default_logger(appname="http_rs")

    def serve(self, sock, request):
        m = re.match(request["route"], request["ressource"])
        path = m.group(1)
        if path.endswith("/"):
            path = path[0:-1]

        if request["method"] == "GET":
            self.get(path, request, sock)
        
        if request["method"] == "PUT":
            self.put(path, request, sock)
        
        if request["method"] == "OPTIONS":
            self.options(path, request, sock)


class config_rest_server(rest_server):
    def __init__(self, config_file="config.json", logger=None):
        super().__init__(logger=logger)
        self.config_file = config_file            
    
    def get(self, path, req, sock):
        config = ep_config.config(self.config_file)
        config.load()
        data = config.get(path)
        self.send_response(sock, code=200, data=data)

    def put(self, path, req, sock):
        config = ep_config.config(self.config_file)
        config.load()
        created = not config.has(path)
        config.set(path, req["fields"])
        config.save()
        if created:
            self.send_response(sock, 201)
        else:
            self.send_response(sock, 200)

    def options(self, path, req, sock):
        header = {"Access-Control-Allow-Methods": "PUT, POST, GET, DELETE, OPTIONS"}
        self.send_response(sock, 200, header=header)


class sensor_rest_server(rest_server):
    def __init__(self, routes, logger=None):
        super().__init__(logger=logger)
        self.routes = routes

    def get(self, path, req, sock):
        reading = ""
        code = 404

        for route in self.routes:
            self.logger.debug("Used route: " + route[0])
            g = re.match(route[0], path)
            if g is not None:
                reading = route[1](path)
                code = 200
                break
                
        self.send_response(sock, code=code, data=reading)
        