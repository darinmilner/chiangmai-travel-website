"""
Tests for SES client
"""
import importlib
from python.clients import ses
from python.clients.ses import SESClient


class TestSESClient:

    def test_init(self, mock_ses):
        importlib.reload(ses)

        client = SESClient()
        assert client.from_email == 'test@example.com'

    def test_send_email_success(self, mock_ses):
        importlib.reload(ses)

        mock_ses.send_raw_email.return_value = {'MessageId': 'test-id'}

        client = SESClient()
        result = client.send_email(
            to=['test@example.com'],
            subject='Test',
            html_body='<h1>Test</h1>',
            text_body='Test body'
        )

        assert result['success'] is True
        assert result['message_id'] == 'test-id'
        assert result['recipients'] == 1
        mock_ses.send_raw_email.assert_called_once()

    def test_send_email_with_cc_bcc(self, mock_ses):
        importlib.reload(ses)

        mock_ses.send_raw_email.return_value = {'MessageId': 'test-id'}

        client = SESClient()
        result = client.send_email(
            to=['to@example.com'],
            subject='Test',
            html_body='<h1>Test</h1>',
            cc=['cc@example.com'],
            bcc=['bcc@example.com']
        )

        assert result['success'] is True
        assert result['recipients'] == 3
        mock_ses.send_raw_email.assert_called_once()

    def test_send_email_error(self, mock_ses):
        importlib.reload(ses)

        mock_ses.send_raw_email.side_effect = Exception('SES error')

        client = SESClient()
        result = client.send_email(
            to=['test@example.com'],
            subject='Test',
            html_body='<h1>Test</h1>'
        )

        assert result['success'] is False
        assert 'SES error' in result['error']