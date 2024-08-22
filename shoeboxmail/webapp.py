import base64
import multiprocessing
import os
import threading

import click
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPOk
from pyramid.view import view_config
from waitress import serve

from shoeboxmail import store

here = os.path.dirname(os.path.abspath(__file__))


@view_config(
    route_name="list",
    renderer="list.jinja2",
)
def list_msgs(request):
    to = request.GET.get("to")
    return dict(
        to=to,
        messages=store.get_msgs(to=to),
    )


@view_config(
    route_name="single",
    renderer="single.jinja2",
)
def single(request):
    msg = store.find(request.matchdict["msg_id"])
    if msg is None:
        return HTTPNotFound()
    return dict(
        message=msg,
    )


@view_config(
    route_name="delete_all",
    request_method="POST",
)
def delete_all(request):
    to = request.POST.get("to", "").strip()
    query = dict()
    if len(to) > 0:
        store.delete_msgs(to=to)
        query["to"] = to
    else:
        store.delete_all()
    return HTTPFound(request.route_path("list", _query=query))


@view_config(
    route_name="delete_msg",
    request_method="POST",
)
def delete_msg(request):
    store.delete_msg(request.matchdict["msg_id"])
    return HTTPFound(request.route_path("list"))


@view_config(
    route_name="api_list",
    request_method="GET",
    renderer="json",
)
def api_list(request):
    to = request.GET.get("to")
    return dict(
        messages=[
            {
                "id": msg.id,
                "to": msg.to,
                "from": msg.from_,
                "replyTo": msg.reply_to,
                "subject": msg.subject,
                "received": f"{msg.received.replace(tzinfo=None).isoformat()}Z",
                "html": msg.html,
                "text": msg.text,
                "attachments": [
                    {
                        "filename": attachment.filename,
                        "content": base64.b64encode(attachment.content).decode("utf-8"),
                        "contentType": attachment.content_type,
                    }
                    for attachment in msg.attachments
                ],
            }
            for msg in store.get_msgs(to=to)
        ],
    )


@view_config(
    route_name="api_single",
    request_method="GET",
    renderer="json",
)
def api_single(request):
    msg = store.find(request.matchdict["msg_id"])
    if msg is None:
        return HTTPNotFound()
    return dict(
        message={
            "id": msg.id,
            "to": msg.to,
            "from": msg.from_,
            "replyTo": msg.reply_to,
            "subject": msg.subject,
            "received": f"{msg.received.isoformat()}Z",
            "html": msg.html,
            "text": msg.text,
            "attachments": [
                {
                    "filename": attachment.filename,
                    "content": base64.b64encode(attachment.content).decode("utf-8"),
                    "contentType": attachment.content_type,
                }
                for attachment in msg.attachments
            ],
        },
    )


@view_config(
    route_name="api_list",
    request_method="DELETE",
)
def api_delete_all(request):
    to = request.GET.get("to", "").strip()
    query = dict()
    if len(to) > 0:
        store.delete_msgs(to=to)
        query["to"] = to
    else:
        store.delete_all()
    return HTTPOk()


@view_config(
    route_name="api_single",
    request_method="DELETE",
)
def api_delete_msg(request):
    store.delete_msg(request.matchdict["msg_id"])
    return HTTPOk()


class MessageReceiverThread(threading.Thread):
    def __init__(self, queue, *args, **kw):
        self.queue = queue
        super().__init__(*args, **kw)

    def run(self):
        click.echo("Starting message receiver thread in HTTP server")
        while True:
            msg = self.queue.get()
            store.add(msg)


class WebAppProcess(multiprocessing.Process):
    def __init__(self, queue, *args, **kw):
        self.queue = queue
        self.receiver = None
        super().__init__(*args, **kw)

    def run(self):
        click.echo("Starting HTTP server")
        settings = {
            "jinja2.directories": os.path.join(here, "templates"),
        }
        config = Configurator(settings=settings)
        config.include("pyramid_jinja2")
        config.add_route("list", "/")
        config.add_route("single", "/message/{msg_id}")
        config.add_route("delete_all", "/delete")
        config.add_route("delete_msg", "/message/{msg_id}/delete")
        config.add_route("api_list", "/api/messages")
        config.add_route("api_single", "/api/messages/{msg_id}")
        config.scan()
        app = config.make_wsgi_app()
        self.receiver = MessageReceiverThread(self.queue)
        self.receiver.start()
        serve(app, listen="*:5577")

    def stop(self):
        click.echo("Stopping HTTP server")
        self.terminate()
