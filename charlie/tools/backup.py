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
    print '---Downloading files ...'
    tmp_dir = os.path.join(data.PACKAGE_DIR, '_tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        ftp = ssh.open_sftp()
        obj = ftp.get(tmp_dir, backup_dir)
        print obj.attr
        ftp.close()
        return True
    except:
        print '---Download failed.'
        return False


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


# ftp = ssh.open_sftp()
#         obj = ftp.put(f1, f2)
#     print '---FTPing zip ...',
#     try:
#         t = str(datetime.now()).replace(' ', '_')
#         if dir[-1] == '/':
#             d = dir + '%s/%s' % (gethostname(), t)
#         else:
#             d = dir + '/%s/%s' % (gethostname(), t)
#         ssh.exec_command('mkdir -p %s' % d)
#         f1 = os.path.join(data.PACKAGE_DIR, '_data.zip')
#         f2 = d + '/_data.zip'
#         ftp = ssh.open_sftp()
#         obj = ftp.put(f1, f2)
#         print obj.attr
#         ftp.close()
#         print 'FTPed to %s' % f2
#     except:
#         print 'FTP failed.'
#         return False
#
#     return True
#
# def get_sftp_details():
#     """
#     To use the sftp method for backup, there must be a file called sftp.txt in
#     charlie/ containing the server address, username, password, and remote
#     directory. This function parses this file and returns those values.
#     """
#     f = os.path.join(data.PACKAGE_DIR, 'sftp.txt')
#     return [l.rstrip() for l in open(f, 'rU').readlines()]
#
#
# def backup(method, attempts):
#     """
#     Backup the data directory now.
#     """
#     print '---Zipping the data directory ...',
#     try:
#         f1 = os.path.join(data.PACKAGE_DIR, '_data.zip')
#         if os.path.exists(f1):
#             os.remove(f1)
#         zipf = zipfile.ZipFile(f1, 'w', zipfile.ZIP_STORED)
#         for root, dirs, files in os.walk(data.DATA_PATH):
#             for _f in files:
#                 _, ext =
#                 zipf.write(os.path.join(root, _f))
#         zipf.close()
#         print 'done.'
#     except:
#         print 'Failed.'
#         return
#     success = False
#     for i in xrange(attempts):
#         if success is False:
#             if method == 'sftp':
#                 success = sftp(*get_sftp_details())
#
#
# if __name__ == '__main__':
#     backup('sftp', 5)
