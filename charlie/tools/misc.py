__author__ = 'smathias'


import os


def is_imgfile(f):
    """
    Checks if the string f is a path to an image file by looking at its
    extension. Does not check the integrity of the file or anything like that.
    :param f:
    :return: bool
    """
    known_fmts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    if os.path.exists(f):
        fn, ext = os.path.splitext(f)
        if ext.lower() in known_fmts:
            return True
        else:
            return False
    else:
        return False