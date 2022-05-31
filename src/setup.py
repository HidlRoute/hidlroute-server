#    Hidl Route - opensource vpn management system
#    Copyright (C) 2023 Dmitry Berezovsky, Alexander Cherednichenko
#    
#    Hidl Route is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    Hidl Route is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import codecs
import os
from os import path

from setuptools import setup, find_packages

src_dir = path.abspath(path.dirname(__file__))
root_dir = path.join(src_dir, '..')

# == Read version ==
version_override = os.environ.get('VERSION_OVERRIDE', None) or None


def read_file(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read_file(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


if not version_override:
    version = get_version("hidlroute/__version__.py")
else:
    print("Using overridden version: " + version_override)
    version = version_override


# == END: Read version ==

def read_requirements(file_name: str):
    with open(file_name, 'r') as f:
        result = f.readlines()
    return list(filter(lambda l: not (l.startswith('#') or l.startswith('--') or '@' in l or l.strip() == ''), result))


# Get the long description from the README file
readme_file = path.join(root_dir, 'docs/pypi-description.md')
try:
    from m2r import parse_from_file

    long_description = parse_from_file(readme_file)
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        long_description = f.read()

# Requirements
requirements_file = path.join(root_dir, 'requirements.txt')
requirements = read_requirements(requirements_file)

setup(
    name='hidlroute-server',
    version=version,
    description='HidlRoute - advanced vpn management system',
    long_description=long_description,
    url='https://github.com/jointbox/jointbox-cli',
    keywords='vpn management server wireguard firewall routing',
    # Author
    author='HidlRoute',
    # License
    license='GPL-3.0-or-later',
    # Technical meta
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Home Automation',

        # License (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        # Python versions support
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>3.8',
    # Structure
    packages=find_packages(include=['hidlroute', 'hidlroute.*', ]),
    install_requires=requirements,
    extras_require={},
    entry_points={
        'console_scripts': [
            'hidlsrv=hidlroute.cli:entrypoint',
        ],
    }
)
