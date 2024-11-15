from functools import wraps
import logging

lg = logging.getLogger()


def log_button_click(func):
    """=== Decorator for logging buttonclicks - by Sziller ==="""
    @wraps(func)  # Preserve the original function's metadata
    def wrapper(self, *args, **kwargs):
        """=== Wrapper =================================================================================================
        Wrapper function that logs the method name before executing the original method.
        :param self:    -   neccessary for the wrapper
        :param args:    -   Positional arguments passed to the original method.
        :param kwargs:  -   Keyword arguments passed to the original method.
        :return: The result of the original method.
        ========================================================================================== by Sziller ==="""
        cim = func.__name__  # Get the method name
        lg.info(f"[clicked     ] - {cim}")
        return func(self, *args, **kwargs)
    return wrapper


def run_internal_reset(func):
    """=== Decorator to run internal method - by Sziller ==="""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """=== Wrapper =================================================================================================
        Wrapper function that runs data reset on parent class.
        :param self:    -   neccessary for the wrapper
        :param args:    -   Positional arguments passed to the original method.
        :param kwargs:  -   Keyword arguments passed to the original method.
        :return: The result of the original method.
        ========================================================================================== by Sziller ==="""
        self._reset_stored_data()  # Run the internal method
        return func(self, *args, **kwargs)
    return wrapper
