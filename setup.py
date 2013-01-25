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


def pkgPath(destination_path, src_path):
    """
        Package up a path recursively
    """
    file_list = []
    if os.path.exists(src_path):
        for root, dirnames, filenames in os.walk(src_path):
            matches = []
            for filename in filenames:
                matches.append(os.path.join(root, filename))
            file_list.append((os.path.join(destination_path, root.replace(src_path, '').strip(os.sep)), matches))

    return file_list

data_files.extend(pkgPath(os.path.join('share', 'diamond', 'collectors'), os.path.join('src', 'collectors')))

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

