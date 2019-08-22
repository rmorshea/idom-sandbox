import ast
import traceback
from io import StringIO

import idom


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
        Icon("cancel", onClick=clear, style={"cursor": "pointer"}, id="clear-stdout"),
        stdout_view,
        style={"width": "100%"},
        id="output-bottom",
    )

    return idom.html.div(ModelView(text, stream), printer, id="output")


@idom.element
async def ModelView(self, text, stdout):
    try:
        view = idom.html.div(eval_exec(text, stdout))
    except Exception as error:
        view = idom.html.pre(
            idom.html.code(
                traceback.format_exc(), style={"color": "rgba(233, 237, 237, 1)"}
            )
        )
    return idom.html.div(view, id="output-top")


def eval_exec(code, stdout):
    block = ast.parse(code, mode="exec")
    validate_ast(block)

    if not block.body or not hasattr(block.body[-1], "value"):
        return idom.html.div()

    last_expr = ast.Expression(block.body.pop().value)

    def _print(*args, **kwargs):
        print(*args, **kwargs, file=stdout)

    context = {"print": _print}
    exec(compile(block, "<string>", mode="exec"), context)
    return eval(compile(last_expr, "<string>", mode="eval"), context)


def validate_ast(tree):
    """It's possible to get past this check, but that doesn't mean you should :)"""
    import_whitelist = {
        "idom",
        "matplotlib",
        # stdlib
        "asyncio",
        "collections",
        "datetime",
        "time",
        "math",
        "functools",
        "itertools",
        "operator",
        "numbers",
        "enum",
        "types",
        "random",
        "statistics",
        "typing",
    }
    builtin_blacklist = {
        "__import__",
        "compile",
        "eval",
        "exec",
        "globals",
        "input",
        "locals",
        "open",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] not in import_whitelist:
                    raise RuntimeError(
                        f"Importing '{alias.name}' is disallowed - "
                        f"you may use {list(sorted(import_whitelist))}"
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.module.split(".", 1)[0] not in import_whitelist:
                raise RuntimeError(
                    f"Importing '{node.module}' is disallowed - "
                    f"you may use {list(sorted(import_whitelist))}"
                )
        elif isinstance(node, ast.Name):
            if node.id in builtin_blacklist:
                raise RuntimeError(f"Builtin '{node.id}' is disallowed")


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


def Icon(name, **attributes):
    style = dict({"color": "rgba(233, 237, 237, 1)"}, **attributes.pop("style", {}))
    return (idom.node("i", name, cls="material-icons", style=style, **attributes),)
