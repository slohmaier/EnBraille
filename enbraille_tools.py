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

def reformatPragraph(paragraph: str, lineLength: int, lineSeperator: str) -> list[str]:
    lines = ['']
    words = paragraph.split(' ')

    if lineLength < 1:
        lines[-1] = ' '.join(words)
    else:
        for word in words:
            lineLen = len(lines[-1])
            wordLen = len(word)

            if lineLen + wordLen + 1 < lineLength:
                lines[-1] += word + ' '
            elif lineLen + wordLen == lineLength:
                lines[-1] += word
                lines.append('')
            else:
                if lineLen - wordLen > 2:
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