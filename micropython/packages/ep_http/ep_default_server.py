import json

class default_server:
    def __init__(self):
        pass

    def send_header(self, sock, header):
        for field in header:
            sock.write(bytes(field + ": " + header[field] + "\r\n", "utf-8"))

    def send_response(self, sock, code=200, header={}, data=None):
        if code == 200: sock.write(b"HTTP/1.1 200 OK\r\n")
        if code == 201: sock.write(b"HTTP/1.1 201 CREATED\r\n")
        if code == 202: sock.write(b"HTTP/1.1 202 ACCEPTED\r\n")
        if code == 204: sock.write(b"HTTP/1.1 204 NO CONTENT\r\n")
        if code == 400: sock.write(b"HTTP/1.1 400 BAD REQUEST\r\n")
        if code == 404: sock.write(b"HTTP/1.1 404 NOT FOUND\r\n")
        if code == 405: sock.write(b"HTTP/1.1 405 METHOD NOT ALLOWED\r\n")

        b_data = b""

        if type(data) is str:
            header["Content-Type"] = "text/plain; charset=UTF-8"
            b_data = bytes(data, "utf-8")
        else:
            if data is not None:
                header["Content-Type"] = "application/json; charset=UTF-8"
                b_data = bytes(json.dumps(data), "utf-8")

        if data is not None:
            header["Content-Length"] = str(len(b_data))

            header["Access-Control-Allow-Origin"] = "http://localhost"
            header["Access-Control-Allow-Headers"] =  "Origin, X-Requested-With, Content-Type, Accept"
            header["Connection"] = "close"

        self.send_header(sock, header)
        
        if data is not None:
            sock.write(b"\r\n")
            sock.write(b_data)