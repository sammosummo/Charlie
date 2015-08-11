"""
Routines for backing up the data to the Olin cluster. These will only work when
the testing computer is connected to the Olin network and therefore not
applicable to any projects run elsewhere.
"""

import filecmp
import os
from shutil import rmtree
from socket import gethostname
import zipfile
import paramiko
import charlie.tools.data as data
from datetime import datetime


def get_sftp_details():
    """
    To use the sftp method for backup, there must be a file called sftp.txt in
    charlie/ containing the server address, username, password, and remote
    directory. This function parses this file and returns those values.
    """
    f = os.path.join(data.PACKAGE_DIR, 'sftp.txt')
    return [l.rstrip() for l in open(f, 'rU').readlines()]


def download_data(server, username, password, backup_dir):
    """
    Back up copies of the raw data files, csvs, and an SQLite database are
    stored in a directory on the backup server. This function will scan and
    download the contents on that directory to a temporary local directory.
    Returns False if unsuccessful and True if successful.
    """
    print '---Establishing connection ...',
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server, username=username, password=password)
        print 'connected!'
    except:
        print 'could not connect.'
        return False
    print '---Attempting to create sftp ...',
    sftp = ssh.open_sftp()
    print 'created!'
    print '---Downloading the following files:'
    for f in sftp.listdir(backup_dir):
        print f,
        remote_f = os.path.join(backup_dir, f)
        local_f = os.path.join(data.BACKUP_DATA_PATH, f)
        try:
            sftp.get(remote_f, local_f)
            print 'success!'
        except:
            print 'failed.'
            return False
    print '---Downloading done.'
    return True


def upload_data(server, username, password, backup_dir):
    """
    Uploads any .data or .csv files in the local data directory to the
    backup server.
    """
    print '---Establishing connection ...',
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server, username=username, password=password)
        print 'connected!'
    except:
        print 'could not connect.'
        return False
    print '---Attempting to create sftp ...',
    sftp = ssh.open_sftp()
    print 'created!'
    print '---Uploading the following files:'
    tmp_files = [f for f in os.listdir(data.BACKUP_DATA_PATH)]
    for p in [data.RAW_DATA_PATH,
              data.CSV_DATA_PATH,
              data.QUESTIONNAIRE_DATA_PATH]:
        d = os.listdir(p)
        for f in d:
            local_f = os.path.join(p, f)
            remote_f = os.path.join(backup_dir, f)
            print f,
            if f not in tmp_files:
                try:
                    sftp.put(local_f, remote_f)
                    print 'success.'
                except:
                    print 'failed.'
                    return False
            else:
                print 'duplicate filename',
                tmp_f = os.path.join(data.BACKUP_DATA_PATH, f)
                if filecmp.cmp(tmp_f, local_f, False) is True:
                    print 'skipped.'
                else:
                    print 'conflict detected',
                    try:
                        s = '_CONFLICT_%s' % str(datetime.now())
                        sftp.put(local_f, remote_f + s)
                        print 'success.'
                    except:
                        print 'failed.'
                        return False
    rmtree(data.BACKUP_DATA_PATH)
    os.makedirs(data.BACKUP_DATA_PATH)
    return True


def backup(method, attempts):
    """
    Backup the data directory now.
    """
    ok = False
    while ok is False:
        ok = download_data(*get_sftp_details())
        attempts -= 1
        if attempts == 0:
            return False
    ok = False
    while ok is False:
        ok = upload_data(*get_sftp_details())
        attempts -= 1
        if attempts == 0:
            return False
    return True



if __name__ == '__main__':
    backup('sftp', 5)
