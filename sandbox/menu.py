import os

import idom

from .utils import STATIC


examples = {}
for file, title in {
    "slideshow.py": "Slideshow",
    "todo.py": "To Do List",
    "dnd.py": "Drag and Drop",
    "snake.py": "The Game Snake",
    "jsx.py": "ReactJS Components",
    # "react.py": "Custom React Components"
}.items():
    with open(os.path.join(STATIC, "examples", file), "r") as f:
        examples[title] = f.read()


@idom.element
async def ExampleButton(self, callback, title, code):
    async def click(event):
        callback(code)

    return idom.html.li(idom.html.a(title), onClick=click)


@idom.element
async def Menu(self, editor, output):
    def update_view(code):
        editor.update(code)
        output.update(code)

    example_buttons = [
        ExampleButton(update_view, title, code) for title, code in examples.items()
    ]

    return idom.html.nav(
        idom.html.ul(
            idom.html.li(
                idom.html.a(
                    "About",
                    href="https://github.com/rmorshea/idom-sandbox",
                    target="_blank",
                )
            ),
            idom.html.li(idom.html.a("Examples"), idom.html.ul(*example_buttons)),
        )
    )
