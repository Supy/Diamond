#!/usr/bin/env python
# coding=utf-8

import os
from glob import glob
import platform
import fnmatch

if os.environ.get('USE_SETUPTOOLS'):
    from setuptools import setup
    setup  # workaround for pyflakes issue #13
    setup_kwargs = dict(zip_safe=0)
else:
    from distutils.core import setup
    setup_kwargs = dict()

data_files = [
    ('share/diamond', ['LICENSE', 'README.md', 'version.txt']),
    ('share/diamond/user_scripts', []),
    ]

distro = platform.dist()[0]
distro_major_version = platform.dist()[1].split('.')[0]

is_virtual_env = os.getenv('VIRTUAL_ENV', False)
config_path = os.environ.get('DIAMOND_CONFIG_PATH', None)
if not config_path:
    if is_virtual_env:
        config_path = os.path.join('etc', 'diamond')
    else:
        if platform.system() == 'Windows':
            root = os.path.splitdrive(sys.executable)[0]
            config_path = os.path.join(root, 'diamond')
        else:
            config_path = os.path.join(os.path.sep, 'etc', 'diamond')

data_files.append((config_path, glob('conf/*.conf.*')))
data_files.append((os.path.join(config_path, 'collectors'), glob('conf/collectors')))
data_files.append((os.path.join(config_path, 'handlers'), glob('conf/handlers')))

if not os.getenv('VIRTUAL_ENV', None):
    if platform.dist()[0] == 'Ubuntu':
        data_files.append(('/etc/init', ['debian/upstart/diamond.conf']))
    if platform.dist()[0] in ['centos', 'redhat']:
        data_files.append(('/etc/init.d', ['bin/init.d/diamond']))
        data_files.append(('/var/log/diamond', ['.keep']))
        if platform.dist()[1].split('.')[0] >= '6':
            data_files.append(('/etc/init', ['rpm/upstart/diamond.conf']))

# Support packages being called differently on different distros
if distro in ['centos', 'redhat']:
    install_requires = ['python-configobj', 'psutil', ],
elif distro == 'debian':
    install_requires = ['python-configobj', 'python-psutil', ],
else:
    install_requires = ['ConfigObj', 'psutil', ],


def get_version():
    """
        Read the version.txt file to get the new version string
        Generate it if version.txt is not available. Generation
        is required for pip installs
    """
    try:
        f = open('version.txt')
    except IOError:
        os.system("./version.sh > version.txt")
        f = open('version.txt')
    version = ''.join(f.readlines()).rstrip()
    f.close()
    return version


def pkgPath(root, path, rpath="/"):
    """
        Package up a path recursively
    """
    global data_files
    if not os.path.exists(path):
        return
    files = []
    for spath in os.listdir(path):
        subpath = os.path.join(path, spath)
        spath = os.path.join(rpath, spath)
        if os.path.isfile(subpath):
            files.append(subpath)

    data_files.append((root + rpath, files))
    for spath in os.listdir(path):
        subpath = os.path.join(path, spath)
        spath = os.path.join(rpath, spath)
        if os.path.isdir(subpath):
            pkgPath(root, subpath, spath)

pkgPath('share/diamond/collectors', 'src/collectors')

version = get_version()

setup(
    name='diamond',
    version=version,
    url='https://github.com/BrightcoveOS/Diamond',
    author='The Diamond Team',
    author_email='https://github.com/BrightcoveOS/Diamond',
    license='MIT License',
    description='Smart data producer for graphite graphing package',
    package_dir={'': 'src'},
    packages=['diamond', 'diamond.handler'],
    scripts=['bin/diamond', 'bin/diamond-setup'],
    data_files=data_files,
    install_requires=install_requires,
    #test_suite='test.main',
    ** setup_kwargs
)

