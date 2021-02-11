import unittest
import ep_logging
import unittest.mock
import io

class Test(unittest.TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def assert_stdout(self, func, expected_output, mock_stdout):
        func()
        if expected_output == "":
            self.assertEqual(mock_stdout.getvalue(), "")
        else:
            self.assertRegex(mock_stdout.getvalue(), expected_output)

    def test_log_default(self):
        logger = ep_logging.default_logger()
        
        for level in range(8):
            logger.level = level
            testcases = [
                (135, lambda: logger.debug("Test"), 7),
                (134, lambda: logger.info("Test"), 6),
                (133, lambda: logger.notice("Test"), 5),
                (132, lambda: logger.warning("Test"), 4),
                (131, lambda: logger.error("Test"), 3),
                (130, lambda: logger.critical("Test"), 2),
                (129, lambda: logger.alarm("Test"), 1),
                (128, lambda: logger.emergency("Test"), 0),
            ]

            for testcase in testcases:
                if level >= testcase[2]:
                    self.assert_stdout(
                        testcase[1], 
                        "<"+str(testcase[0])+">1 \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.0Z esp32 logger - - Test\n"
                        )
                else:
                    self.assert_stdout(testcase[1], "")
        