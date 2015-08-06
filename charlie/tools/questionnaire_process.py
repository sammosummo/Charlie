__version__ = 2.0
__author__ = 'Sam Mathias'


from datetime import datetime
import sqlite3
import pandas
import charlie.tools.data as data
import charlie.tools.summaries as summaries
import charlie.tools.arguments as arguments
import charlie.tools.questionnaires


def summarise_bis11(form):
    """
    Analysis of bis11 data. Returns a new form dict with summaries computed and
    missing items as empty values.
    """
    subscales = {
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

    for subscale, items in subscales.iteritems():

            if all(item in form for item, _ in items):

                score = 0
                for item, reverse in items:
                    if reverse is False:
                        score += int(form[item])
                    else:
                        score -= int(form[item])
                form[subscale] = score

            else:

                form[subscale] = 'some items missing; could not calculate'
    for item, _ in items:
        if item not in form:
            form[item] = ''
    return form


def summarise_dass(form):
    """
    Analysis of dass data. Returns a new form dict with summaries computed and
    missing items as empty values.
    """
    subscales = {
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
    for subscale, items in subscales.iteritems():

            if all(item in form for item in items):

                form[subscale] = sum(int(form[item]) for item in items)

            else:

                form[subscale] = 'some items missing; could not calculate'
    for item in items:
        if item not in form:
            form[item] = ''
    return form


def summarise_stai(form):
    """
    Analysis of stai data. Returns a new form dict with summaries computed and
    missing items as empty values.
    """
    scorecard = {
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
    if all(item in form for item in scorecard):

        a_score = 0
        b_score = 0

        for item, reverse in scorecard.iteritems():
            n = int(item.split('_')[1])
            if n <= 20:
                this_score = a_score
            else:
                this_score = b_score
            if reverse is False:
               this_score += int(form[item])
            else:
                this_score -= int(form[item])
        form['stai_a_total'] = a_score
        form['stai_b_total'] = b_score
    else:
        form['stai_a_total'] = 'some items missing; could not calculate'
        form['stai_b_total'] = 'some items missing; could not calculate'
    for item in scorecard:
        if item not in form:
            form[item] = ''
    return form


def summarise_bdi2(form):
    """
    Analysis of bdi2 data. Returns a new form dict with summaries computed and
    missing items as empty values.
    """
    intr = lambda s: int(s.replace('a', '').replace('b', ''))
    items = ['bdi2_%i' % i for i in xrange(1, 22)]

    if all(item in form for item in items):

        form['bdi2_total'] = sum(intr(form[item]) for item in items)

    else:

        form['bdi2_total'] = 'some items missing; could not calculate'
    for item in items:
        if item not in form:
            form[item] = ''
    return form


def summarise_fnds(form):
    """
    Analysis of fnds data. Returns a new form dict with summaries computed and
    missing items as empty values.
    """
    items = ['fnds_%i' % i for i in xrange(7)]

    if all(item in form for item in items):

        if int(form['fnds_0']) == 1:

            form['fnds_score'] = sum(int(form[item]) for item in items)

        else:

            form['fnds_score'] = 'error: items completed but indicated non-smoking'

    elif 'fnds_0' in items:

        if int(form['fnds_0']) == 1:

            form['fnds_score'] = 'some items missing; could not calculate'

        else:

            form['fnds_score'] = 'non-smoking'

    else:

        form['fnds_score'] = 'some items missing; could not calculate'

    for item in items:
        if item not in form:
            form[item] = ''
    return form


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def process_form_data(form):
    """
    Analyse the form data and save to the local db
    """
    args = arguments.get_args()
    quickfix = lambda f: f.replace('\n', '').replace('\r', '')
    qlist = args.questionnaires.split()
    _qlist = []
    for q in qlist:
        try:
            _q = data.pj(data.QUESTIONNAIRES_PATH, q + '.txt')
            f = open(_q, 'rU').readlines()
            _qlist += f
        except:
             _qlist.append(q)
        qlist = [quickfix(l) for l in _qlist]
    for q_name in qlist:
        data_obj = data.Data(
            args.proband_id,
            args.lang,
            args.user_id,
            args.proj_id,
            q_name,
            None
        )
        data_obj.date_done = datetime.now()
        _stats = summaries.get_universal_stats(data_obj)
        _func = globals()['summarise_%s' % q_name]
        _form = _func(form)
        _stats += [(k, v) for k, v in _form.iteritems()]
        df = summaries.make_df(_stats)
        if args.proband_id != 'TEST':
            f = '%s_%s.csv' % (args.proband_id, q_name)
            df.to_csv(data.pj(data.QUESTIONNAIRE_DATA_PATH, f))
            con = sqlite3.connect(data.LOCAL_DB_F)
            try:
                df.to_sql(q_name, con, index=False, if_exists='fail')
            except:
                s = 'SELECT * from %s' % q_name
                df2 = pandas.read_sql(s, con, index_col=None)
                df3 = pandas.concat([df, df2])
                df3 = df3.drop_duplicates()
                df3.to_sql(q_name, con, index=False, if_exists='replace')
            con.close()
