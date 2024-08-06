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

    def test_auto_strip_tags(self):
        """Test HTML is stripped for text content."""
        send_html_email(
            subject='Test',
            html_content='<h1>Title</h1><p>Paragraph</p>',
            to=['test@example.com'],
        )

        body = mail.outbox[0].body
        assert '<h1>' not in body
        assert 'Title' in body


class TestSendTemplateEmail:
    """Test cases for send_template_email function."""

    @patch('django_extensions.email_utils.utils.render_to_string')
    def test_renders_template(self, mock_render):
        """Test template is rendered."""
        mock_render.return_value = '<h1>Hello John</h1>'

        send_template_email(
            subject='Welcome',
            template_name='email/welcome.html',
            context={'name': 'John'},
            to=['user@example.com'],
        )

        mock_render.assert_called()
        assert mock_render.call_args[0][0] == 'email/welcome.html'
        assert mock_render.call_args[0][1] == {'name': 'John'}


class TestEmailBuilder:
    """Test cases for EmailBuilder class."""

    def test_basic_builder(self):
        """Test basic email building."""
        result = (
            EmailBuilder()
            .subject('Test Subject')
            .to('user@example.com')
            .html('<p>Content</p>')
            .send()
        )

        assert result == 1
        assert mail.outbox[0].subject == 'Test Subject'

    def test_method_chaining(self):
        """Test method chaining works."""
        builder = (
            EmailBuilder()
            .subject('Test')
            .to('user1@example.com')
            .to('user2@example.com')
            .cc('cc@example.com')
            .bcc('bcc@example.com')
            .from_email('sender@example.com')
            .reply_to('reply@example.com')
            .html('<p>Content</p>')
        )

        preview = builder.preview()

        assert preview['subject'] == 'Test'
        assert len(preview['to']) == 2
        assert 'cc@example.com' in preview['cc']

    def test_to_with_list(self):
        """Test to() accepts list."""
        builder = EmailBuilder().to(['a@x.com', 'b@x.com'])
        assert 'a@x.com' in builder._to
        assert 'b@x.com' in builder._to

    def test_missing_content_raises(self):
        """Test missing content raises error."""
        builder = EmailBuilder().subject('Test').to('user@example.com')

        with pytest.raises(ValueError, match='content'):
            builder.send()

    def test_missing_recipient_raises(self):
        """Test missing recipient raises error."""
        builder = EmailBuilder().subject('Test').html('<p>Content</p>')

        with pytest.raises(ValueError, match='recipient'):
            builder.send()

    def test_preview(self):
        """Test preview method."""
        preview = (
            EmailBuilder()
            .subject('Test')
            .to('user@example.com')
            .html('<p>Content</p>')
            .preview()
        )

        assert preview['subject'] == 'Test'
        assert preview['to'] == ['user@example.com']
        assert '<p>' in preview['html_content']
        assert '<p>' not in preview['text_content']

    def test_attach(self):
        """Test adding attachments."""
        builder = (
            EmailBuilder()
            .subject('Test')
            .to('user@example.com')
            .html('<p>Content</p>')
            .attach('file.txt', b'content', 'text/plain')
        )

        assert len(builder._attachments) == 1

    @patch('django_extensions.email_utils.utils.render_to_string')
    def test_template(self, mock_render):
        """Test template method."""
        mock_render.return_value = '<p>Rendered</p>'

        builder = EmailBuilder().template('email.html', {'key': 'value'})

        mock_render.assert_called_once_with('email.html', {'key': 'value'})
        assert builder._html_content == '<p>Rendered</p>'
