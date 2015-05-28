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


def backup_to_olin():
    """
    Backs up the local data directory from this machine to the Olin cluster
    using my username and password. The data from each machine is saved in
    within a zip:

    /home/Smathias/onrc/data/charlie-data/<machine_name>/<datetime>/_data.zip

    If this function fails to backup the data, it will return False. It it
    succeeds, it will return True.
    """
    print '---Zipping the data directory ...',
    try:
        f1 = os.path.join(data.PACKAGE_DIR, '_data.zip')
        if os.path.exists(f1):
            os.remove(f1)
        zipf = zipfile.ZipFile(f1, 'w')
        for root, dirs, files in os.walk(data.DATA_PATH):
            for _f in files:
                zipf.write(os.path.join(root, _f))
        zipf.close()
        print 'done.'
    except:
        print 'Failed.'
        return False

    print '---Establishing connection ...',
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('compute01', username='Smathias', password='ZSiy16^*')
        print 'connected!'
    except:
        print 'could not connect.'
        return False

    print '---FTPing zip ...',
    try:
        d = '/home/Smathias/onrc/data/charlie-data/%s' % gethostname()
        ssh.exec_command('mkdir %s' % d)
        t = str(datetime.now()).replace(' ', '_')
        d = d + '/%s' % t
        ssh.exec_command('mkdir %s' % d)
        f2 = d + '/_data.zip'
        ftp = ssh.open_sftp()
        ftp.put(f1, f2)
        ftp.close()
        print 'FTPed.'
    except:
        print 'FTP failed.'
        return False

    return True


if __name__ == '__main__':
    backup_to_olin()
