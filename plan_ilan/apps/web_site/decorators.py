import logging
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return view_func(request, *args, **kwargs)

    return wrapper_func


def authenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect('home')

    return wrapper_func


# pre save handler for subclasses
# https://web.archive.org/web/20120715042306/http://codeblogging.net/blogs/1/14

def get_subclasses(classes, level=0):
    """
        Return the list of all subclasses given class (or list of classes) has.
        Inspired by this question:
        http://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-given-class-in-python
    """
    # for convenience, only one class can can be accepted as argument
    # converting to list if this is the case
    if not isinstance(classes, list):
        classes = [classes]

    if level < len(classes):
        classes += classes[level].__subclasses__()
        return get_subclasses(classes, level + 1)
    else:
        return classes


def receiver_subclasses(signal, sender, dispatch_uid_prefix, weak=True, **kwargs):
    """
    A decorator for connecting receivers and all receiver's subclasses to signals. Used by passing in the
    signal and keyword arguments to connect::

        @receiver_subclasses(post_save, sender=MyModel)
        def signal_receiver(sender, **kwargs):
            ...
    """

    def _decorator(func):
        all_senders = get_subclasses(sender)
        logger.debug(f'got subclasses {all_senders} for sender {sender}')
        for snd in all_senders:
            signal.connect(func, sender=snd, weak=weak, dispatch_uid=f'{dispatch_uid_prefix}_{snd.__name__}', **kwargs)
        return func
    return _decorator
