import sys
from enbraille_functions.reformat import EnBrailleReformater

if __name__ == '__main__':
    r = EnBrailleReformater(sys.argv[1])
    print(r.filename)
    print('maxLength')
    print(r._maxLineLength)
    print('pageLengths')
    print(r.pageLength)
