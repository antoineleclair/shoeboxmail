import email
import threading
from datetime import datetime, timezone
from email import policy
from email.message import EmailMessage
from typing import cast

import click
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import (
    SMTP as SMTPServer,
    Envelope as SMTPEnvelope,
    Session as SMTPSession,
)

from shoeboxmail.store import Attachment, Message


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
                raise Exception(  # pylint: disable=broad-exception-raised
                    "Emtpy content"
                )
            msg = cast(
                EmailMessage,
                email.message_from_bytes(
                    envelope.original_content,
                    policy=policy.default,
                    _class=EmailMessage,
                ),
            )
            new = Message(
                to=msg["To"],
                from_=msg["From"],
                reply_to=msg["ReplyTo"],
                subject=msg["Subject"],
                received=datetime.now(timezone.utc),
                html=None,
                text=None,
                attachments=[],
            )
            click.echo(f"Received email for {new.to}: {new.subject}")
            if msg.is_multipart():
                for part in msg.walk():
                    if part.is_attachment():
                        filename = part.get_filename()
                        content_type = part.get_content_type()
                        assert filename is not None
                        assert content_type is not None
                        attachment = Attachment(
                            filename=filename,
                            content_type=content_type,
                            content=cast(bytes, part.get_payload(decode=True)),
                        )
                        new.attachments.append(attachment)
                    else:
                        mime = part.get_content_type()
                        if mime == "text/html":
                            new.html = cast(
                                bytes, part.get_payload(decode=True)
                            ).decode("utf-8")
                        elif mime == "text/plain":
                            new.text = cast(
                                bytes, part.get_payload(decode=True)
                            ).decode("utf-8")
            else:
                mime = msg.get_content_type()
                if mime == "text/html":
                    new.html = cast(bytes, msg.get_payload(decode=True)).decode("utf-8")
                elif mime == "text/plain":
                    new.text = cast(bytes, msg.get_payload(decode=True)).decode("utf-8")
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
