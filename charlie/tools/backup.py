"""
Routines for backing up the data to the Olin cluster. These will only work when
the testing computer is connected to the Olin network and therefore not
applicable to any projects run elsewhere.
"""

from datetime import datetime
import os
from socket import gethostname
import zipfile
import paramiko
import charlie.tools.data as data


def sftp(server, username, password, dir):
    """
    Backs up the local data directory via secure ftp. Returns False if fails
    and True if successful.
    """
    print '---Establishing connection ...',
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, username=username, password=password)
        print 'connected!'
    except:
        print 'could not connect.'
        return False

    print '---FTPing zip ...',
    try:
        t = str(datetime.now()).replace(' ', '_')
        if dir[-1] == '/':
            d = dir + '%s/%s' % (gethostname(), t)
        else:
            d = dir + '/%s/%s' % (gethostname(), t)
        ssh.exec_command('mkdir -p %s' % d)
        f1 = os.path.join(data.PACKAGE_DIR, '_data.zip')
        f2 = d + '/_data.zip'
        ftp = ssh.open_sftp()
        print os.path.exists(f1)

        ftp.put(f1, f2)
        ftp.close()
        print 'FTPed.'
    except:
        print 'FTP failed.'
        return False

    return True

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
    print '---Zipping the data directory ...',
    try:
        f1 = os.path.join(data.PACKAGE_DIR, '_data.zip')
        if os.path.exists(f1):
            os.remove(f1)
        zipf = zipfile.ZipFile(f1, 'w', zipfile.ZIP_STORED)
        for root, dirs, files in os.walk(data.DATA_PATH):
            for _f in files:
                zipf.write(os.path.join(root, _f))
        zipf.close()
        print 'done.'
    except:
        print 'Failed.'
        return
    success = False
    for i in xrange(attempts):
        if success is False:
            if method == 'sftp':
                success = sftp(*get_sftp_details())


if __name__ == '__main__':
    backup('sftp', 5)
