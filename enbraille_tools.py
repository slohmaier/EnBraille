import logging

def reformatPragraph(paragraph: str, lineLength: int, lineSeperator: str) -> list[str]:
    lines = []
    paraLen = len(paragraph)
    i = 0
    while i < paraLen:
        addSeperator = False

        #move start of new line to none whitespace
        while paragraph[i].isspace() and i < paraLen:
            i += 1
        
        #move back of new line until non whitespace
        endi = i + lineLength - 1
        if endi >= paraLen:
            endi = paraLen -1
        while paragraph[endi].isspace() and endi > i:
            endi -= 1
        
        #seperate non-whitesapce word
        if endi + 1 < paraLen and not paragraph[endi].isspace():
            endi -= 1
            addSeperator = True
        

        line = paragraph[i:endi]

        if addSeperator:
            line += lineSeperator
        
        lines.append(line)
        i = endi + 1

    return lines

_BREILLENUMS = {'0': 'j', '1': 'a', '2': 'b', '3': 'c', '4': 'd', '5': 'e', '6': 'f', '7': 'g', '8': 'h', '9': 'i'}

def generateOutput(lines: list[str], pageLength: int, lineLength: int) -> str:
    output = ''
    lineno = 1
    for line in lines:
        output += line + '\n'

        if pageLength > 0 and lineno % pageLength == 0:
            pageStr = '#{}'.format( int(lineno / pageLength) + 1 )
            for s, n in _BREILLENUMS.items():
                pageStr = pageStr.replace(s, n)
            output += ' ' * (lineLength - len(pageStr) - 1) + pageStr + '\n'
            lineno += 1

        lineno += 1
    return output