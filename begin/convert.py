"Type casting for function arguments"
from __future__ import absolute_import, division, print_function
import functools

try:
    from inspect import signature
except ImportError:
    from begin.funcsigs import signature


def convert(**mappings):
    """Cast function arguments to decorated function.

    Optionally use callables to cast the arguments for the decorated functions.

    >>> import begin
    >>> @begin.convert(second=int)
    ... def func(first, second=None):
    ...     pass

    If a value is passed as the 'second' argument to 'func', it will be
    replaced with the result of calling the 'int' function with the value. If
    no value is passed, the default value will be used without casting.

    Casting also works for variable position arguments. In this case the
    casting function is called on each argument.

    >>> @begin.convert(args=float)
    ... def func(*args):
    ...    pass

    Helper functions for casting arguments can be found in the 'begin.utils'
    module.
    """
    def decorator(func):
        target = func
        while hasattr(target, '__wrapped__'):
            target = getattr(func, '__wrapped__')
        sig = signature(target)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args = list(args)
            for pos, param in enumerate(sig.parameters.values()):
                if param.name not in mappings:
                    continue
                if param.kind == param.POSITIONAL_ONLY:
                    args[pos] = mappings[param.name](args[pos])
                if param.kind == param.POSITIONAL_OR_KEYWORD:
                    if param.name in kwargs and \
                            kwargs[param.name] is not param.default:
                        kwargs[param.name] = mappings[param.name](
                                kwargs[param.name])
                    elif pos < len(args) and \
                            args[pos] is not param.default:
                        args[pos] = mappings[param.name](args[pos])
                if param.kind == param.KEYWORD_ONLY and \
                        kwargs[param.name] is not param.default:
                    kwargs[param.name] = mappings[param.name](
                            kwargs[param.name])
                if param.kind == param.VAR_POSITIONAL:
                    start = pos
                    for pos in range(start, len(args)):
                        args[pos] = mappings[param.name](args[pos])
                if param.kind == param.VAR_KEYWORD:
                    msg = 'Variable length keyword arguments not supported'
                    raise ValueError(msg)
            return func(*args, **kwargs)
        if not hasattr(wrapper, '__wrapped__'):
            wrapper.__wrapped__ = func
        return wrapper
    return decorator
