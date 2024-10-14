import unittest
from unittest.mock import patch, MagicMock
import json
import logging
from loki_logger import LokiLogger, get_loki_logger

class TestLokiLogger(unittest.TestCase):

    def setUp(self):
        self.logger = get_loki_logger("TestLogger")

    @patch('loki_logger.requests.post')
    def test_log_info(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.logger.info("Test info message", org_id="org123", bot_id="bot456")

        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        self.assertIn('json', call_args)
        log_data = call_args['json']
        
        self.assertEqual(len(log_data['streams']), 1)
        stream = log_data['streams'][0]
        self.assertEqual(stream['stream']['level'], 'info')
        self.assertEqual(len(stream['values']), 1)
        log_entry = json.loads(stream['values'][0][1])
        self.assertEqual(log_entry['message'], '"Test info message"')
        self.assertEqual(log_entry['level'], 'info')

    @patch('loki_logger.requests.post')
    def test_log_error_with_trace(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.logger.error("Test error message", org_id="org789", bot_id="bot012", trace="Error trace")

        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        self.assertIn('json', call_args)
        log_data = call_args['json']
        
        stream = log_data['streams'][0]
        self.assertEqual(stream['stream']['level'], 'error')
        log_entry = json.loads(stream['values'][0][1])
        self.assertEqual(log_entry['message'], '"Test error message"')
        self.assertEqual(log_entry['level'], 'error')
        self.assertEqual(log_entry['trace'], 'Error trace')

    @patch('loki_logger.requests.post')
    def test_log_with_dict_message(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        test_dict = {"key1": "value1", "key2": 2}
        self.logger.info(test_dict, org_id="org123", bot_id="bot456")

        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        log_data = call_args['json']
        
        stream = log_data['streams'][0]
        log_entry = json.loads(stream['values'][0][1])
        self.assertEqual(json.loads(log_entry['message']), test_dict)

    @patch('loki_logger.requests.post')
    def test_log_levels(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        log_levels = ['debug', 'info', 'warning', 'error']
        for level in log_levels:
            getattr(self.logger, level)(f"Test {level} message", org_id="org123", bot_id="bot456")

            mock_post.assert_called()
            call_args = mock_post.call_args[1]
            log_data = call_args['json']
            
            stream = log_data['streams'][0]
            self.assertEqual(stream['stream']['level'], level)
            log_entry = json.loads(stream['values'][0][1])
            self.assertEqual(log_entry['level'], level)
            self.assertEqual(log_entry['message'], f'"Test {level} message"')

            mock_post.reset_mock()

    @patch('loki_logger.requests.post')
    def test_request_exception(self, mock_post):
        mock_post.side_effect = Exception("Test exception")

        # Capture stdout to check the error message
        with self.assertLogs(level='ERROR') as cm:
            self.logger.info("Test message", org_id="org123", bot_id="bot456")

        self.assertIn("Error pushing logs to Loki: Test exception", cm.output[0])

if __name__ == '__main__':
    unittest.main()