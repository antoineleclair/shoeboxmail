import email
import threading
from datetime import datetime, timezone
from email import policy

import click
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import (
    SMTP as SMTPServer,
    Envelope as SMTPEnvelope,
    Session as SMTPSession,
)

from shoeboxmail.store import Message


class SMTPHandler:  # pylint: disable=too-few-public-methods
    def __init__(self, queue):
        self.queue = queue

    async def handle_DATA(
        self,
        server: SMTPServer,  # pylint: disable=unused-argument
        session: SMTPSession,  # pylint: disable=unused-argument
        envelope: SMTPEnvelope,
    ) -> str:
        try:
            if envelope.original_content is None:
                raise Exception(
                    "Emtpy content"
                )  # pylint: disable=broad-exception-raised
            msg = email.message_from_bytes(
                envelope.original_content, policy=policy.default
            )
            new = Message(
                to=msg["To"],
                from_=msg["From"],
                reply_to=msg["ReplyTo"],
                subject=msg["Subject"],
                received=datetime.now(timezone.utc),
                html=None,
                text=None,
            )
            click.echo(f"Received email for {new.to}: {new.subject}")
            if msg.is_multipart():
                for part in msg.walk():
                    mime = part.get_content_type()
                    if mime == "text/html":
                        new.html = part.get_content()  # type:ignore[attr-defined]
                    elif mime == "text/plain":
                        new.text = part.get_content()  # type:ignore[attr-defined]
            else:
                mime = msg.get_content_type()
                if mime == "text/html":
                    new.html = msg.get_content()  # type:ignore[attr-defined]
                elif mime == "text/plain":
                    new.text = msg.get_content()  # type:ignore[attr-defined]
            self.queue.put(new)
            return "250 OK"
        except Exception as ex:  # pylint: disable=broad-except
            click.echo("Failed to process email")
            click.echo(ex)
            return "500 Could not process your message"


class SMTPThread(threading.Thread):
    def __init__(self, queue, *args, **kw):
        self.queue = queue
        self.server = None
        super().__init__(*args, **kw)

    def run(self):
        click.echo("Starting SMTP server")
        handler = SMTPHandler(queue=self.queue)
        self.server = Controller(handler, hostname="0.0.0.0", port=5566)
        self.server.start()

    def stop(self):
        click.echo("Stopping SMTP server")
        self.server.stop()
        self.join()
