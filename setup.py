from distutils.core import setup

setup(
    name='Charlie',
    version='1.0.0',
    packages=['charlie', 'charlie.gui', 'charlie.tests', 'charlie.tools'],
    url='http://www.srmathias.com',
    license='',
    author='Samuel Mathias',
    author_email='samuel.mathias@gmail.com',
    description='Charlie is a free neurocognitive test battery written in Python.',
    install_requires=['numpy', 'scipy', 'pygame', 'pandas', 'web.py', 'paramiko']
)
