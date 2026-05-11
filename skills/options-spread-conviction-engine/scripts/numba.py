# Mock numba module for Python 3.14+ compatibility
# pandas_ta requires numba but numba doesn't support Python 3.14 yet
# This provides a fallback that just executes the function normally

def njit(*args, **kwargs):
    """No-Just-In-Time compiler decorator fallback.
    
    When numba is not available, this simply returns the original function
    without compilation, allowing pandas_ta to work in pure Python mode.
    """
    def decorator(func):
        return func
    
    # Handle both @njit and @njit() syntax
    if args and callable(args[0]):
        return args[0]
    return decorator

# Other numba exports that pandas_ta might use
class types:
    pass

class cuda:
    pass

def jit(*args, **kwargs):
    def decorator(func):
        return func
    if args and callable(args[0]):
        return args[0]
    return decorator

def vectorize(*args, **kwargs):
    def decorator(func):
        return func
    if args and callable(args[0]):
        return args[0]
    return decorator

def guvectorize(*args, **kwargs):
    def decorator(func):
        return func
    if args and callable(args[0]):
        return args[0]
    return decorator
