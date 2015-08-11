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
    The raw data are all stored in a directory on the Olin cluster. This function
    will download the contents of this folder to a local directory. This allows
    us to check for duplicates within the local data set, and only upload those
    that are new. Returns False if unsuccessful and True if successful.
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
    tmp_dir = os.path.join(data.PACKAGE_DIR, '_tmp')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    print '---Attempting to create sftp ...',
    ftp = ssh.open_sftp()
    print 'created!'
    for i in ftp.listdir(backup_dir):
        lstatout  = str(ftp.lstat(i)).split()[0]
        print ftp.lstatlstatout


def compare_raw_data():
    """
    Returns two lists. The first contains paths of all the raw data files
    in the data directory, minus those that already appear in the
    temporarily downloaded data directory.  The second contains conflict
    files (one with that filename exists, but is not an exact match).
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
