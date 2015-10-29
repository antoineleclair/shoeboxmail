import smtpd
import threading
import email
import asyncore
from datetime import datetime
import click


class SMTPServer(smtpd.SMTPServer):

    def process_message(self, peer, mailfrom, rcpttos, data):
        try:
            msg = email.message_from_string(data)
            new = {
                'to': msg['To'],
                'from': msg['From'],
                'subject': msg['Subject'],
                'received': datetime.utcnow(),
                }
            click.echo('Received email for {}: {}'.format(new['to'],
                                                          new['subject']))
            if msg.is_multipart():
                for part in msg.walk():
                    mime = part.get_content_type()
                    if mime == 'text/html':
                        new['html'] = part.get_payload()
                    elif mime == 'text/plain':
                        new['text'] = part.get_payload()
            # TODO store.add(new)
        except Exception as ex:
            click.echo('Failed to process email')
            click.echo(ex)


class SMTPThread(threading.Thread):

    def run(self):
        click.echo('Starting SMTP server')
        self.server = SMTPServer(('0.0.0.0', 5566), None)
        asyncore.loop(timeout=0.5)

    def stop(self):
        click.echo('Stopping SMTP server')
        self.server.close()
        self.join()
