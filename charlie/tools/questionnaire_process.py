"""
Administers a set of questionnaires.

"""

__version__ = 0.1
__author__ = 'Sam Mathias'


from datetime import datetime
from copy import copy
import cPickle
import sqlite3
import sys
import webbrowser
import numpy as np
import pandas
import web
import charlie.tools.data as data
import charlie.tools.summaries as summaries
import charlie.tools.arguments as arguments
from os import listdir


bis_subscales = {
   'attention': [
       ('bis11_5', False), ('bis11_9', True), ('bis11_11', False),
       ('bis11_28', False)
   ],
   'motor': [
       ('bis11_2', False), ('bis11_3', False), ('bis11_4', False),
       ('bis11_17', False), ('bis11_19', False), ('bis11_22', False),
       ('bis11_25', False)
   ],
   'selfcontrol': [
       ('bis11_1', True), ('bis11_7', True), ('bis11_8', True),
       ('bis11_12', True), ('bis11_13', True), ('bis11_14', False)
   ],
   'cognitivecomplexity': [
       ('bis11_10', True), ('bis11_15', True), ('bis11_18', False),
       ('bis11_27', False), ('bis11_29', True)
   ],
   'perserverance': [
       ('bis11_16', False), ('bis11_21', False), ('bis11_23', False),
       ('bis11_30', True)
   ],
   'congitiveinstability': [
       ('bis11_6', False), ('bis11_24', False), ('bis11_26', False)
   ],
   'attentionalimpulsiveness': [
       ('bis11_6', False), ('bis11_5', False), ('bis11_9', True),
       ('bis11_11', False), ('bis11_20', True), ('bis11_24', False),
       ('bis11_26', False), ('bis11_28', False)
   ],
   'motorimpulsiveness': [
       ('bis11_2', False), ('bis11_3', False), ('bis11_4', False),
       ('bis11_16', False), ('bis11_17', False), ('bis11_19', False),
       ('bis11_21', False), ('bis11_22', False), ('bis11_23', False),
       ('bis11_25', False), ('bis11_30', True)
   ],
   'nonplanningimpulsiveness': [
       ('bis11_1', True), ('bis11_7', True), ('bis11_8', True),
       ('bis11_10', True), ('bis11_12', True), ('bis11_13', True),
       ('bis11_14', False), ('bis11_15', True), ('bis11_18', False),
       ('bis11_27', False), ('bis11_29', True)
   ]
}

dass_subscales = {
    'depression': [
        'dass_3', 'dass_5', 'dass_10', 'dass_13', 'dass_16', 'dass_17',
        'dass_21', 'dass_24', 'dass_26', 'dass_31', 'dass_34', 'dass_37',
        'dass_38', 'dass_42'
    ],
    'anxiety': [
        'dass_2', 'dass_4', 'dass_7', 'dass_9', 'dass_15', 'dass_19',
        'dass_20', 'dass_23', 'dass_25', 'dass_28', 'dass_30', 'dass_36',
        'dass_40', 'dass_41'
    ],
    'stress': [
        'dass_1', 'dass_6', 'dass_8', 'dass_11', 'dass_12', 'dass_14',
        'dass_18', 'dass_22', 'dass_27', 'dass_29', 'dass_32', 'dass_33',
        'dass_35', 'dass_39'
    ]
}

stai_scorecard = {
    'stai_1': True, 'stai_2': True, 'stai_3': False, 'stai_4': False,
    'stai_5': True, 'stai_6': False, 'stai_7': False, 'stai_8': True,
    'stai_9': False, 'stai_10': True, 'stai_11': True, 'stai_12': False,
    'stai_13': False, 'stai_14': False, 'stai_15': True, 'stai_16': True,
    'stai_17': False, 'stai_18': False, 'stai_19': True, 'stai_20': True,
    'stai_21': True, 'stai_22': False, 'stai_23': True, 'stai_24': False,
    'stai_25': False, 'stai_26': True, 'stai_27': True, 'stai_28': False,
    'stai_29': False, 'stai_30': True, 'stai_31': False, 'stai_32': False,
    'stai_33': True, 'stai_34': True, 'stai_35': False, 'stai_36': True,
    'stai_37': False, 'stai_38': False, 'stai_39': True, 'stai_40': False
}


def process_form_data(form):
    """
    Converts the contents of form (a dictionary-like object) to a pure
    dictionary, calculated additional stats are required, and returns a list of
    pandas data frames. Summary stats for the specific questionnaires are hard
    coded in this module.
    """
    new_form = {}
    new_form.update(form)

    questionnaires_in_form = set([a.split('_')[0] for a in new_form])

    if 'bdi2' in questionnaires_in_form:
        try:
            _form = {k: v for k, v in form.iteritems() if 'bdi2' in k}
            _int = lambda s: int(s.replace('a', '').replace('b', ''))
            bdi_q = {k: _int(v) for k, v in _form.iteritems()}
            new_form['bdi2_total'] = sum(bdi_q.values())
        except:
            new_form['bdi2_total'] = ''

    if 'bis11' in questionnaires_in_form:

        for subscale, items in bis_subscales.iteritems():
            try:
                score = 0
                for item, reverse in items:
                    if reverse is False:
                        score += int(form[item])
                    else:
                        score -= int(form[item])
                new_form['bis11_' + subscale] = score
            except:
                new_form['bis11_' + subscale] = ''

    if 'dass' in questionnaires_in_form:

        for subscale, items in dass_subscales.iteritems():
            try:
                score = 0
                for item in items:
                    score += int(form[item])
                new_form['dass_' + subscale] = score
            except:
                new_form['dass_' + subscale] = ''

    if 'stai' in questionnaires_in_form:

        try:
            a_score = 0
            b_score = 0
            for item, reverse in stai_scorecard.iteritems():
                n = int(item.split('_')[1])
                if n <= 20:
                    this_score = a_score
                else:
                    this_score = b_score
                if reverse is False:
                    this_score += int(form[item])
                else:
                    this_score -= int(form[item])
            new_form['stai_a_total'] = a_score
            new_form['stai_b_total'] = b_score
        except:
            new_form['stai_a_total'] = ''
            new_form['stai_b_total'] = ''

    if 'fnds_0' in questionnaires_in_form:

        score = 0
        if int(form['fnds_0']) == 1:

            for i in xrange(1, 7):

                if 'fnds_%i' % i in form:

                    score += int(form['fnds_%i' % i])
                else:
                    form['fnds_%i' % i] = ''

        new_form['fnds_score'] = score

    dfs = {}
    for q_name in questionnaires_in_form:
        stats = [(k, v) for k, v in new_form.iteritems() if q_name in k]
        dfs[q_name] = summaries.make_df(stats)

    return dfs


def to_db(dfs):
    """
    Saves the questionnaire data frames to the local cb.
    """
    args = arguments.get_args()
    con = sqlite3.connect(data.LOCAL_DB_F)
    for q_name, df in dfs.iteritems():
        data_obj = data.Data(
            args.proband_id,
            args.lang,
            args.user_id,
            args.proj_id,
            q_name,
            None
        )
        data_obj.date_done = datetime.now()
        stats = summaries.get_universal_stats(data_obj)
        df = pandas.concat([summaries.make_df(stats), df], axis=1)
        if args.proband_id != 'TEST':
            df.to_sql(q_name, con, index=False, if_exists='append')
