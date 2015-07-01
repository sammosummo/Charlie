"""
Script for renaming and re-saving proband data.
"""


__author__ = 'smathias'


import cPickle
import os


def rename_proband(data_obj, new_id, path=None):
    """
    Renames a proband ID and returns a new raw object. Optionally saves the
    new raw object to the given path.
    """
    if isinstance(data_obj, basestring) is True:
        data_obj = cPickle.load(open(data_obj))
    data_obj.proband_id = new_id
    new_data = []
    for trial in data_obj.data:
        new_trial = list(trial)
        new_trial[0] = new_id
        new_trial = tuple(new_trial)
        new_data.append(new_trial)
    data_obj.data = new_data
    if path is not None:
        if os.path.exists(path):
            f = '%s_%s.data' % (data_obj.proband_id, data_obj.test_name)
            f = os.path.join(path, f)
            cPickle.dump(data_obj, open(f, 'w'))
    return data_obj


def test():
    """
    Try out rename_proband.
    """
    path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    path = os.path.join(path, 'data')
    for f in os.listdir(os.path.join(path, '4398')):
        data_obj = os.path.join(path, '4398', f)
        rename_proband(data_obj, '4398', path)


if __name__ == '__main__':
    test()