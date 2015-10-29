import time
import click
from .smtpserver import SMTPThread
from .webapp import WebAppThread


@click.command()
def cli():
    try:
        smtp_thread = SMTPThread()
        smtp_thread.start()
        webapp_thread = WebAppThread()
        webapp_thread.start()
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        click.echo('Exiting...')
        smtp_thread.stop()
        webapp_thread.stop()
