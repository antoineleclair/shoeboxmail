import signal
import time
import multiprocessing
import click
from .smtpserver import SMTPThread
from .webapp import WebAppProcess


should_stop = False

@click.command()
def cli():
    global should_stop
    try:
        queue = multiprocessing.Queue()
        smtp_thread = SMTPThread(queue)
        smtp_thread.start()
        webapp_thread = WebAppProcess(queue)
        webapp_thread.start()
        should_stop = False
        def received_sigterm(signum, frame):
            global should_stop
            click.echo('Received SIGTERM signal.')
            should_stop = True
        signal.signal(signal.SIGTERM, received_sigterm)
        while True:
            if should_stop:
                break
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        click.echo('Exiting...')
        smtp_thread.stop()
        webapp_thread.stop()
