import logging

def reformatPragraph(paragraph: str, lineLength: int, lineSeperator: str) -> list[str]:
    lines = ['']
    words = paragraph.split(' ')

    for word in words:
        lineLen = len(lines[-1])
        wordLen = len(word)

        if lineLen + wordLen + 1 <= lineLength:
            lines[-1] += word + ' '
        else:
            if lineLen - wordLen <= 2:
                splitPos = lineLength - 1 - lineLen
                lines[-1] += word[:splitPos] + lineSeperator
                word = word[splitPos:]
            
            while len(word) > lineLength:
                lines.append(word[:lineLength-1] + lineSeperator)
                word = word[lineLength-1:]
            lines.append(word + ' ')

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