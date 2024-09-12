#
# Copyright (c) 2024 Stefan Lohmaier.
#
# This file is part of EnBraille 
# (see https://github.com/slohmaier/EnBraille).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from setuptools import setup
import pyinstaller
import pyinstaller_dmg

# PyInstaller options
pyinstaller_options = [
    '--name=EnBraille',
    '--windowed',
    '--icon=icon.ico',
    '--add-data=liblouis/*;liblouis',
]

# PyInstaller DMG options
pyinstaller_dmg_options = {
    'applications_shortcut': True,
    'background_image': 'background.png',
    'icon_locations': {
        'EnBraille.app': (128, 128),
    },
}

setup(
    name='EnBraille',
    version='1.0',
    author='Stefan Lohmaier',
    description='EnBraille App',
    app=['enbraille_main.py'],
    data_files=[
        ('.', ['icon.ico', 'background.png']),
    ],
    options={
        'pyinstaller': pyinstaller_options,
        'pyinstaller-dmg': pyinstaller_dmg_options,
    },
    setup_requires=[
        'pyinstaller',
        'pyinstaller-dmg',
    ],
)
