import os

from idom import Element

here = os.path.dirname(__file__)
STATIC = os.path.join(here, "static")
SESSION_TIME_LIMIT = 30 * 60  # 30 minutes


def custom_element(cls, state=None):

    def setup(function):

        def constructor(*args, **kwargs):
            element = cls(function, state, False)
            element.update(*args, **kwargs)
            return element

        return constructor

    return setup
