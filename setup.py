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
    author='Your Name',
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
