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
    
    embrailledata = EnBrailleData(app)
    for n in dir(embrailledata):
        if n.startswith('refor'):
            sys.stderr.write('{}: {}\n'.format(n, getattr(embrailledata, n)))
    d = Dummy()
    print(r.reformat(d.progress, embrailledata))
