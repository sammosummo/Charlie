"""
Parse the command-line arguments.
"""

import argparse


def get_parser():
    """
    Returns a parser object that allows an individual test or a batch of tests
    to accept arguments from the command line.
    """
    description = 'Charlie: A neuropsychological test battery'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        '-p', '--proband_id', default='TEST',
        help='Proband ID (if omitted, no data will be saved).'
    )
    parser.add_argument(
        '-l', '--lang', choices=['EN'], default='EN',
        help='Testing language (only EN works right now).'
    )
    parser.add_argument(
        '-u', '--user_id', default='',
        help='Experimenter/user ID.'
    )
    parser.add_argument(
        '-b', '--batch_file', default='',
        help='Name of a batch or path to a batch file.'
    )
    parser.add_argument(
        '-j', '--proj_id', default='',
        help='Project ID.'
    )
    parser.add_argument(
        '-t', '--test_name', default='',
        help='Individual test name (ignored if -b included).'
    )
    parser.add_argument(
        '-q', '--questionnaires', default='',
        help='Names of questionnaires or name of questionnaire list.'
    )
    parser.add_argument(
        '-g', '--gui', action="store_true",
        help='Load the GUI (overrides other options).'
    )
    parser.add_argument(
        '-a', '--backup', choices=['', 'sftp'], default='',
        help="Backup method (e.g., 'sftp')"
    )
    return parser


def get_args():
    """
    Retrieve all command-line arguments.
    """
    return get_parser().parse_args()
