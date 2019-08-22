import os

import idom

from .utils import STATIC


with open(os.path.join(STATIC, "editor.js"), "r") as f:
    editor = idom.Module(f.read())


@idom.element(state="output")
async def Editor(self, text, output):
    async def change(new):
        output.update(new)

    return idom.html.div(
        editor.Editor(
            value=text,
            options={"theme": "material", "mode": "python", "indentUnit": 4},
            onChange=change,
        ),
        id="editor",
    )
