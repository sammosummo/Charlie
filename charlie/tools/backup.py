"""
Routines for backing up the data to the Olin cluster. These will only work when
the testing computer is connected to the Olin network and therefore not
applicable to any projects run elsewhere.
"""

import filecmp
import os
from socket import gethostname
import zipfile
import paramiko
import charlie.tools.data as data
from datetime import datetime


def download_data(server, username, password, backup_dir):
    """
    Back up copies of the raw data files, csvs, and an SQLite database are
    stored in a directory on the Olin cluster. This function will scan and
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
    for f in sftp.listdir(backup_dir):
        abs_f = os.path.join(backup_dir ,f)
        try:
            sftp.get(abs_f, data.BACKUP_DATA_PATH)
        except:
            return False
    return True


def upload_data():
    """
    Attempts to transfer the contents of the local data directory to the Olin
    cluster. Before uploading, every file is checked with the
    """
    local_files = [f for f in os.listdir(data.RAW_DATA_PATH)]
    tmp_dir = os.path.join(data.PACKAGE_DIR, '_tmp')
    remote_files = [f for f in os.listdir(tmp_dir)]
    unique_files = []
    conflict_files = []
    for f in local_files:
        if f not in remote_files:
            unique_files.append(f)
        else:
            same = filecmp.cmp(
                os.path.join(data.RAW_DATA_PATH, f),
                os.path.join(tmp_dir, f)
            )
            if same is False:
                conflict_files.append(f)
    return unique_files, conflict_files


def upload_data(server, username, password, backup_dir,
               unique_files, conflict_files):
    print '---Establishing connection ...',
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server, username=username, password=password)
        print 'connected!'
    except:
        print 'could not connect.'
        return False
    print '---Downloading files ...'
    tmp_dir = os.path.join(data.PACKAGE_DIR, '_tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        ftp = ssh.open_sftp()
        for f in unique_files:
            f1 = os.path.join(data.RAW_DATA_PATH, f)
            obj = ftp.put(tmp_dir, backup_dir)
        print obj.attr
        ftp.close()
        return True
    except:
        print '---Download failed.'
        return False


def get_sftp_details():
    """
    To use the sftp method for backup, there must be a file called sftp.txt in
    charlie/ containing the server address, username, password, and remote
    directory. This function parses this file and returns those values.
    """
    f = os.path.join(data.PACKAGE_DIR, 'sftp.txt')
    return [l.rstrip() for l in open(f, 'rU').readlines()]


def backup(method, attempts):
    """
    Backup the data directory now.
    """
    for attempt in xrange(attempts):
        download_data(*get_sftp_details())



if __name__ == '__main__':
    backup('sftp', 5)
