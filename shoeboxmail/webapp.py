import multiprocessing
import threading
import os
from wsgiref.simple_server import make_server, WSGIServer
from waitress import serve
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import click
from . import store


here = os.path.dirname(os.path.abspath(__file__))

@view_config(
    route_name='list',
    renderer='list.jinja2',
    )
def list_msgs(request):
    to = request.GET.get('to')
    return dict(
        to=to,
        messages=store.get_msgs(to=to),
        )

@view_config(
    route_name='single',
    renderer='single.jinja2',
    )
def single(request):
    msg = store.find(request.matchdict['msg_id'])
    if msg is None:
        return HTTPNotFound()
    return dict(
        message=msg,
        )


@view_config(
    route_name='delete_all',
    request_method='POST',
    )
def delete_all(request):
    to = request.POST.get('to', '').strip()
    query = dict()
    if len(to) > 0:
      store.delete_msgs(to=to)
      query['to'] = to
    else:
      store.delete_all()
    return HTTPFound(request.route_path('list', _query=query))

@view_config(
    route_name='delete_msg',
    request_method='POST',
    )
def delete_msg(request):
    store.delete_msg(request.matchdict['msg_id'])
    return HTTPFound(request.route_path('list'))


class MessageReceiverThread(threading.Thread):

    def __init__(self, queue, *args, **kw):
        self.queue = queue
        super().__init__(*args, **kw)

    def run(self):
        click.echo('Starting message receiver thread in HTTP server')
        while True:
            msg = self.queue.get()
            store.add(msg)


class WebAppProcess(multiprocessing.Process):

    def __init__(self, queue, *args, **kw):
        self.queue = queue
        super().__init__(*args, **kw)

    def run(self):
        click.echo('Starting HTTP server')
        settings = {
            'jinja2.directories': os.path.join(here, 'templates'),
            }
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.add_route('list', '/')
        config.add_route('single', '/message/{msg_id}')
        config.add_route('delete_all', '/delete')
        config.add_route('delete_msg', '/message/{msg_id}/delete')
        config.scan()
        app = config.make_wsgi_app()
        self.receiver = MessageReceiverThread(self.queue)
        self.receiver.start()
        serve(app, listen='*:5577')

    def stop(self):
        click.echo('Stopping HTTP server')
        self.terminate()
