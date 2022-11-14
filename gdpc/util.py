""" Generic utilities """


import sys


def eprint(*args, **kwargs):
    """ print(), but to stderr """
    print(*args, file=sys.stderr, **kwargs)
