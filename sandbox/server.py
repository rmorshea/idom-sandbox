import json
import asyncio
import traceback
import multiprocessing as multi

from sanic.response import redirect
from idom.server.sanic import PerClientState
from idom.core.layout import Layout
from idom.core.render import SingleStateRenderer

from .utils import SESSION_TIME_LIMIT


class SandboxServer(PerClientState):
    def _setup_application(self, app, config):
        super()._setup_application(app, config)

        @app.route("/")
        async def to_client(request):
            return redirect("/client/index.html")

    async def _run_renderer(self, send, recv):
        ctx = multi.get_context("spawn")
        inner_pipe, outer_pipe = aiopipe(ctx)

        async def forward_send():
            while True:
                await send(await outer_pipe.recv())

        async def forward_recv():
            while True:
                await outer_pipe.send(await recv())

        proc = ctx.Process(
            target=render_element_in_loop,
            args=(
                self._element_constructor,
                self._element_args,
                self._element_kwargs,
                inner_pipe,
            ),
            daemon=True,
        )
        proc.start()

        try:
            await asyncio.wait_for(
                asyncio.gather(forward_send(), forward_recv()), SESSION_TIME_LIMIT
            )
        finally:
            proc.terminate()


def aiopipe(ctx):
    c1, c2 = ctx.Pipe()
    return AsyncPipe(c1), AsyncPipe(c2)


class AsyncPipe:
    def __init__(self, conn):
        self._conn = conn

    async def send(self, data):
        self._conn.send(data)

    async def recv(self):
        while not self._conn.poll():
            await asyncio.sleep(0.01)
        return self._conn.recv()


class CustomLayout(Layout):

    __slots__ = ("_model_view_element", "_output_element")

    def set_output_view(self, element):
        self._output_element = element

    async def trigger(self, target, data):
        try:
            return await super().trigger(target, data)
        except Exception as error:
            self._output_element.update(None, last_error=traceback.format_exc())

    async def render(self):
        try:
            return await super().render()
        except Exception as error:
            self._output_element.update(None, last_error=traceback.format_exc())
            return await super().render()


def render_element_in_loop(constructor, args, kwargs, pipe):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    layout = CustomLayout(constructor(*args, **kwargs))
    renderer = SingleStateRenderer(layout)
    loop.run_until_complete(renderer.run(pipe.send, pipe.recv, None))
