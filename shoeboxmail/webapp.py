import threading
import os
from wsgiref.simple_server import make_server
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
def list(request):
    return dict(
        messages=store.get_all(),
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
    store.delete_all()
    return HTTPFound(request.route_path('list'))

@view_config(
    route_name='delete_msg',
    request_method='POST',
    )
def delete_msg(request):
    store.delete_msg(request.matchdict['msg_id'])
    return HTTPFound(request.route_path('list'))


class WebAppThread(threading.Thread):

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
        self.server = make_server('0.0.0.0', 5577, app)
        self.server.serve_forever()

    def stop(self):
        click.echo('Stopping HTTP server')
        self.server.shutdown()
        self.join()
