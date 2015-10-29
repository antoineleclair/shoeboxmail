import time
import click
from .smtpserver import SMTPThread
import asyncore


@click.command()
def cli():
    try:
        smtp_thread = SMTPThread()
        smtp_thread.start()
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        click.echo('Exiting...')
        smtp_thread.stop()
