import os
import ast
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

    url = f"https://picsum.photos/800/300?image={index}"
    return idom.node("img", src=url, onClick=update_image)

Slideshow()
"""[1:]


def exec_then_eval(code):
    block = ast.parse(code, mode="exec")

    # assumes last node is an expression
    last = ast.Expression(block.body.pop().value)

    context = {}
    exec(compile(block, "<string>", mode="exec"), context)
    return eval(compile(last, "<string>", mode="eval"), context)


@idom.element
async def Sandbox(self, text):
    output = Output(text)
    return idom.html.div(
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
                min-width: 650px;
                height: 100%;
                margin-right: 10px;
            }
            #output {
                height: 100%;
                float: left;
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
        return idom.html.p(str(error))


class SandboxServer(PerClientState):

    def _setup_application(self, app, config):
        super()._setup_application(app, config)
        @app.route("/")
        async def to_client(request):
            return redirect("/client/index.html")


SandboxServer(Sandbox, example).run("0.0.0.0", int(os.environ.get("PORT", 8765)))
