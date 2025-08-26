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
import logging
import sys
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication
from enbraille_data import EnBrailleData
from enbraille_functions.reformat import EnBrailleReformater

class Dummy(QObject):
    def progress(self, perc, msg):
        return

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    r = EnBrailleReformater(sys.argv[1])
    sys.stderr.write(r.filename+'\n')
    sys.stderr.write('maxLength'+'\n')
    sys.stderr.write(str(r._maxLineLength)+'\n')
    sys.stderr.write('pageLengths'+'\n')
    sys.stderr.write(str(r.pageLength)+'\n')
    
    app = QApplication([sys.argv[0]])
    app.setApplicationName("EnBraille")
    app.setOrganizationName("slohmaier")
    app.setOrganizationDomain("slohmaier.de")
    app.setApplicationVersion("0.1.0")
    
    enbrailledata = EnBrailleData(app)
    for n in dir(enbrailledata):
        if n.startswith('refor'):
            sys.stderr.write('{}: {}\n'.format(n, getattr(enbrailledata, n)))
    d = Dummy()
    logging.info("Reformat result: %s", r.reformat(d.progress, enbrailledata))
