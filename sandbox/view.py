import time
import asyncio

import idom

from .output import Output
from .menu import Menu, examples
from .editor import Editor
from .style import stylesheets
from .server import SandboxServer
from .utils import STATIC, SESSION_TIME_LIMIT


@idom.element
async def SandboxView(self):
    output = Output(examples["Slideshow"])
    editor = Editor(examples["Slideshow"], output)
    sandbox = idom.html.div(editor, output, id="sandbox")
    return idom.html.div(stylesheets, TimeoutCountdown(), Menu(editor, output), sandbox)


@idom.element
async def TimeoutCountdown(self, remainder=(SESSION_TIME_LIMIT - 10)):
    now = time.time()

    async def delayed_update(delay):
        await asyncio.sleep(delay)
        future = time.time()
        diff = future - now
        self.update(remainder - diff)

    if remainder < 0:
        return idom.html.h3(
            f"You session is expiring...",
            style={"color": "rgba(233, 237, 237, 1)", "width": "100%"},
        )
    if remainder <= 60:
        asyncio.ensure_future(delayed_update(1))
        return idom.html.h3(
            f"You session will expire in {int(remainder)} seconds.",
            style={"color": "rgba(233, 237, 237, 1)", "width": "100%"},
        )
    elif remainder <= (5 * 60):
        asyncio.ensure_future(delayed_update(10))
        return idom.html.h3(
            f"You session will expire in {(remainder // 30) / 2} minutes.",
            style={"color": "rgba(233, 237, 237, 1)", "width": "100%"},
        )
    else:
        asyncio.ensure_future(delayed_update(60))
        return idom.html.div()
