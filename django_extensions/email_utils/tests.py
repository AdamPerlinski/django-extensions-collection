"""Tests for email utilities."""

import pytest
from django.core import mail
from unittest.mock import patch, MagicMock

from .utils import send_html_email, send_template_email, EmailBuilder


class TestSendHtmlEmail:
    """Test cases for send_html_email function."""

    def test_basic_email(self):
        """Test sending basic HTML email."""
        result = send_html_email(
            subject='Test Subject',
            html_content='<h1>Hello</h1>',
            to=['test@example.com'],
        )

        assert result == 1
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == 'Test Subject'
        assert 'Hello' in mail.outbox[0].body

    def test_html_alternative(self):
        """Test HTML content is attached as alternative."""
        send_html_email(
            subject='Test',
            html_content='<h1>Hello</h1>',
            to=['test@example.com'],
        )

        email = mail.outbox[0]
        alternatives = email.alternatives
        assert len(alternatives) == 1
        assert alternatives[0][1] == 'text/html'

    def test_multiple_recipients(self):
        """Test sending to multiple recipients."""
        send_html_email(
            subject='Test',
            html_content='<p>Content</p>',
            to=['user1@example.com', 'user2@example.com'],
        )

        assert mail.outbox[0].to == ['user1@example.com', 'user2@example.com']

    def test_string_recipient(self):
        """Test string recipient is converted to list."""
        send_html_email(
            subject='Test',
            html_content='<p>Content</p>',
            to='single@example.com',
        )

        assert mail.outbox[0].to == ['single@example.com']

    def test_cc_and_bcc(self):
        """Test CC and BCC recipients."""
        send_html_email(
            subject='Test',
            html_content='<p>Content</p>',
            to=['main@example.com'],
            cc=['cc@example.com'],
            bcc=['bcc@example.com'],
        )

        email = mail.outbox[0]
        assert email.cc == ['cc@example.com']
        assert email.bcc == ['bcc@example.com']

    def test_custom_text_content(self):
        """Test custom plain text content."""
        send_html_email(
            subject='Test',
            html_content='<p>HTML Content</p>',
            text_content='Plain text content',
            to=['test@example.com'],
        )

        assert mail.outbox[0].body == 'Plain text content'

