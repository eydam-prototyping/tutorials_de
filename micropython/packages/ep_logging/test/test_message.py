import unittest
import ep_logging


class Test(unittest.TestCase):
    def test_str(self):

        m = ep_logging.message(msg="Testmessage", timestamp=(2021, 1, 20, 18, 48, 0))
        self.assertEqual(str(m),'<133>1 2021-01-20T18:48:00.0Z esp32 logger - - Testmessage')

        m = ep_logging.message(msg="Testmessage", timestamp=(2021, 1, 20, 18, 48, 0), servity=3)
        self.assertEqual(str(m),'<131>1 2021-01-20T18:48:00.0Z esp32 logger - - Testmessage')

        m = ep_logging.message(msg="Testmessage", timestamp=(2021, 1, 20, 18, 48, 0), facility=5)
        self.assertEqual(str(m),'<45>1 2021-01-20T18:48:00.0Z esp32 logger - - Testmessage')

        m = ep_logging.message(msg="Testmessage", timestamp=(2021, 1, 20, 18, 48, 0), appname="unittest")
        self.assertEqual(str(m),'<133>1 2021-01-20T18:48:00.0Z esp32 unittest - - Testmessage')

        m = ep_logging.message(msg="Testmessage", timestamp=(2021, 1, 20, 18, 48, 0), msgid="MSG123")
        self.assertEqual(str(m),'<133>1 2021-01-20T18:48:00.0Z esp32 logger - MSG123 Testmessage')

        m = ep_logging.message(msg="Testmessage", timestamp=(2021, 1, 20, 18, 48, 0), procid=5)
        self.assertEqual(str(m),'<133>1 2021-01-20T18:48:00.0Z esp32 logger 5 - Testmessage')