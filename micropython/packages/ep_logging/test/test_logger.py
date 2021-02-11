import unittest
import ep_logging
import socket
import threading
import concurrent.futures

class Test(unittest.TestCase):
    def udp_listen(self, server_socket):
        while True:
            message, address = server_socket.recvfrom(1024)
            if message != "":
                return message

    def _test_func(self, func, port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', port))
        return_value = ""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.udp_listen, (server_socket))
            func()
            return_value = future.result()
        server_socket.close()
        return return_value.decode("ascii")

    def test_log(self):
        port = 514
        l = ep_logging.syslog_logger("localhost", port=port)
        l2 = ep_logging.colored_logger()
        l2.alarm("Test")
"""
        for x in [
            (lambda: l.emergency("Test"), 0),
            (lambda: l.alert("Test"), 1),
            (lambda: l.critical("Test"), 2),
            (lambda: l.error("Test"), 3),
            (lambda: l.warning("Test"), 4),
            (lambda: l.notice("Test"), 5),
            (lambda: l.info("Test"), 6),
            (lambda: l.debug("Test"), 7)
            ]:
            res = self._test_func(func=x[0], port=port)
            m = ep_logging.message(msg="Test", servity=x[1])
            self.assertEqual(res, str(m))"""