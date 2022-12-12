import asyncore  # pylint: disable=deprecated-module
import email
import smtpd  # pylint: disable=deprecated-module
import threading
from datetime import datetime
from email import policy

import click

from shoeboxmail.store import Message


class SMTPServer(smtpd.SMTPServer):
    def __init__(self, queue, *args, **kw):
        self.queue = queue
        super().__init__(*args, **kw)

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        try:
            msg = email.message_from_bytes(data, policy=policy.default)
            new = Message(
                to=msg["To"],
                from_=msg["From"],
                reply_to=msg["ReplyTo"],
                subject=msg["Subject"],
                received=datetime.utcnow(),
                html=None,
                text=None,
            )
            click.echo(f"Received email for {new.to}: {new.subject}")
            if msg.is_multipart():
                for part in msg.walk():
                    mime = part.get_content_type()
                    if mime == "text/html":
                        new.html = part.get_content()
                    elif mime == "text/plain":
                        new.text = part.get_content()
            else:
                mime = msg.get_content_type()
                if mime == "text/html":
                    new.html = msg.get_content()
                elif mime == "text/plain":
                    new.text = msg.get_content()
            self.queue.put(new)
        except Exception as ex:  # pylint: disable=broad-except
            click.echo("Failed to process email")
            click.echo(ex)


class SMTPThread(threading.Thread):
    def __init__(self, queue, *args, **kw):
        self.queue = queue
        self.server = None
        super().__init__(*args, **kw)

    def run(self):
        click.echo("Starting SMTP server")
        self.server = SMTPServer(self.queue, ("0.0.0.0", 5566), None)
        asyncore.loop(timeout=0.5)

    def stop(self):
        click.echo("Stopping SMTP server")
        self.server.close()
        self.join()
