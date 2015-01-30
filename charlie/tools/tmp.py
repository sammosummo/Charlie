__author__ = 'smathias'


def get_accuracy_stats(df, prefix='', ans_col='ans', rsp_col='rsp'):
    """
    Calculates number of trials, number and proportion of correct trials.
    :param df: pandas.DataFrame
    :param prefix: str
    :param ans_col: str
    :param rsp_col: str
    :return: (cols, entries)
    """
