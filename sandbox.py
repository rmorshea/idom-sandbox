import os
import ast
import traceback

from sanic.response import redirect

import idom
from idom.server.sanic import PerClientState


with open("editor.js", "r") as f:
    src = idom.Module(f.read())

example = """
import idom

@idom.element
async def Slideshow(self, index=0):

    async def update_image(event):
        self.update(index + 1)

    return idom.html.img(
        src=f"https://picsum.photos/500/300?image={index}",
        onClick=update_image,
        width="100%",
    )

Slideshow()
"""[1:]


def exec_then_eval(code):
    block = ast.parse(code, mode="exec")

    if not block.body or not hasattr(block.body[-1], "value"):
        return idom.html.div()

    last_expr = ast.Expression(block.body.pop().value)

    context = {}
    exec(compile(block, "<string>", mode="exec"), context)
    return eval(compile(last_expr, "<string>", mode="eval"), context)


def info():
    return idom.html.div(
        idom.html.link(
            href="https://fonts.googleapis.com/icon?family=Material+Icons",
            rel="stylesheet",
        ),
        idom.html.a(
            idom.node("i", "info", cls="material-icons", style={"color": "rgba(233, 237, 237, 1)"}),
            href="https://github.com/rmorshea/idom-sandbox",
            target="_blank",
            id="info",
        )
    )


@idom.element
async def Sandbox(self, text):
    output = Output(text)
    return idom.html.div(
        info(),
        Editor(text, output),
        output,
        idom.html.style("""
            html, body, #root, #root > div {
                height: 100%;
            }
            #root {
                padding: 10px;
            }
            body {
                background-color: #263238;
            }
            .CodeMirror {
                height: auto;
                border-left: 1px solid rgb(83,127,126);
                border-right: 1px solid rgb(83,127,126);
            }
            #editor {
                box-sizing: border-box;
                float: left;
                min-width: 300px;
                margin-right: 10px;
            }
            #output {
                min-width: 300px;
                float: left;
            }
            #info {
                float: right;
            }
        """)
    )


@idom.element
async def Editor(self, text, output):
    async def change(new):
        output.update(new)

    return idom.html.div(
        idom.html.link(
            rel="stylesheet",
            type="text/css",
            href="https://codemirror.net/lib/codemirror.css",
        ),
        idom.html.link(
            rel="stylesheet",
            type="text/css",
            href="https://codemirror.net/theme/material.css",
        ),
        src.Editor(
            value=text,
            options={
                "theme": "material",
                "mode": "python",
                "indentUnit": 4,
                "lineNumbers": True,
            },
            onChange=change,
        ),
        id="editor",
    )


@idom.element
async def Output(self, text):
    try:
        return idom.html.div(exec_then_eval(text), id="output")
    except Exception as error:
        return idom.html.pre(
            idom.html.code(
                traceback.format_exc(),
                style={"color": "rgba(233, 237, 237, 1)"},
            ),
            id="output",
        )


class SandboxServer(PerClientState):

    def _setup_application(self, app, config):
        super()._setup_application(app, config)
        @app.route("/")
        async def to_client(request):
            return redirect("/client/index.html")


SandboxServer(Sandbox, example).run("0.0.0.0", int(os.environ.get("PORT", 5000)))
