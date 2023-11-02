from typing import Callable
import warnings


class MCException(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__()
        self.message = message
        self.status_code = status_code


def deprecated(func: Callable) -> Callable:
    # This is a decorator which can be used to mark functions as deprecated. It will result in a
    # warning being emitted when the function is used.
    def new_func(*args, **kwargs):  # type: ignore[no-untyped-def]
        warnings.warn(f"Call to deprecated function {func.__name__}.", category=DeprecationWarning)
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func
