"""
This script contains methods for summarising the data from several
questionnaires.

"""

__version__ = 0.1
__author__ = 'smathias'


import numpy as np
import pandas
import charlie.tools.data as data

def summarise_bdi(form):
    """
    Create summary for the Beck Depression Inventory.
    """
    new_dict = {k: v for k, v in form.iteritems() if 'bdi2' in k}




    questionnaire_data = filter('bdi2', questionnaire_data)
    for k, v in questionnaire_data.iteritems():
        if v == 'Please choose ...':
            questionnaire_data[k] = np.nan