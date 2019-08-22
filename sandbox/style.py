import os

import idom

from .utils import STATIC


styles_from_file = []

with open(os.path.join(STATIC, "style.css"), "r") as f:
    styles_from_file.append(f.read())

with open(os.path.join(STATIC, "nav.css"), "r") as f:
    styles_from_file.append(f.read())

stylesheets = idom.html.div(
    idom.html.link(rel="stylesheet", href="https://codemirror.net/lib/codemirror.css"),
    idom.html.link(rel="stylesheet", href="https://codemirror.net/theme/material.css"),
    idom.html.link(
        rel="stylesheet", href="https://fonts.googleapis.com/icon?family=Material+Icons"
    ),
    *list(map(idom.html.style, styles_from_file))
)
