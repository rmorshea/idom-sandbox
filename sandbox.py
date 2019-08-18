import os
import ast
import sys
import traceback
from io import StringIO

from sanic.response import redirect

import idom
from idom.server.sanic import PerClientState


with open("static/editor.js", "r") as f:
    editor = idom.Module(f.read())

with open("static/example.py", "r") as f:
    simple_example = f.read()

with open("static/style.css", "r") as f:
    global_style = idom.html.div(
        idom.html.link(
            rel="stylesheet",
            href="https://codemirror.net/lib/codemirror.css",
        ),
        idom.html.link(
            rel="stylesheet",
            href="https://codemirror.net/theme/material.css",
        ),
        idom.html.link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/icon?family=Material+Icons",
        ),
        idom.html.style(f.read()),
    )


def exec_then_eval(code, stdout):
    block = ast.parse(code, mode="exec")

    if not block.body or not hasattr(block.body[-1], "value"):
        return idom.html.div()

    last_expr = ast.Expression(block.body.pop().value)

    def _print(*args, **kwargs):
        print(*args, **kwargs, file=stdout)

    context = {"print": _print}
    exec(compile(block, "<string>", mode="exec"), context)
    return eval(compile(last_expr, "<string>", mode="eval"), context)


@idom.element
async def Sandbox(self, text):
    output = Output(text)
    sandbox = idom.html.div(Editor(text, output), output, id="sandbox")
    return idom.html.div(global_style, sandbox)


@idom.element
async def Editor(self, text, output):
    async def change(new):
        output.update(new)

    return idom.html.div(
        editor.Editor(
            value=text,
            options={
                "theme": "material",
                "mode": "python",
                "indentUnit": 4,
            },
            onChange=change,
        ),
        id="editor",
    )


@idom.element
async def Output(self, text):
    stdout_view = StdoutView()

    def on_print(stream):
        stdout_view.update(stream.getvalue())

    stream = CaptureIO(on_print)

    async def clear(event):
        stream.truncate(0)
        stream.seek(0)
        stdout_view.update(stream.getvalue())

    printer = idom.html.div(
        stdout_view,
        Icon("cancel", onClick=clear, style={"cursor": "pointer"}, id="clear-stdout"),
        style={"width": "100%"},
        id="output-bottom",
    )

    return idom.html.div(ModelView(text, stream), printer, id="output")


@idom.element
async def ModelView(self, text, stdout):
    try:
        view = idom.html.div(exec_then_eval(text, stdout))
    except Exception as error:
        view = idom.html.pre(
            idom.html.code(
                traceback.format_exc(), style={"color": "rgba(233, 237, 237, 1)"}
            )
        )
    return idom.html.div(
        idom.html.div(view, id="model-view"),
        idom.html.a(
            Icon("info", id="info"),
            href="https://github.com/rmorshea/idom-sandbox",
            target="_blank",
        ),
        id="output-top",
    )


@idom.element
async def StdoutView(self, text=""):
    return idom.html.pre(
        idom.html.code(text), style={"color": "rgba(233, 237, 237, 1)", "float": "left"}
    )


class CaptureIO(StringIO):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def write(self, *args, **kwargs):
        result = super().write(*args, **kwargs)
        self._callback(self)
        return result


class SandboxServer(PerClientState):
    def _setup_application(self, app, config):
        super()._setup_application(app, config)

        @app.route("/")
        async def to_client(request):
            return redirect("/client/index.html")


def Icon(name, **attributes):
    style = dict({"color": "rgba(233, 237, 237, 1)"}, **attributes.pop("style", {}))
    return (idom.node("i", name, cls="material-icons", style=style, **attributes),)


SandboxServer(Sandbox, simple_example).run("0.0.0.0", int(os.environ.get("PORT", 5000)))
