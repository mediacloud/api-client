import warnings


class MCException(Exception):
    def __init__(self, message, status_code=0):
        self.message = message
        self.status_code = status_code


def deprecated(func):
    # This is a decorator which can be used to mark functions as deprecated. It will result in a
    # warning being emitted when the function is used.
    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning)
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func
