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
import os
import re
import zipfile
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote
from xml.etree import ElementTree as ET


def epub2md(file: str) -> str:
    epub = Epub(file)
    epub.initialize()
    markdown = ''
    for i in epub.contents:
        content = epub.file.open(i).read()
        content = content.decode("utf-8")
        parser = MDFilter()
        try:
            parser.feed(content)
            parser.close()
        except Exception as e:
            raise e
        
        markdown += parser.markdown()
    return markdown

class MDFilter(HTMLParser):
    _headerRegex = re.compile(r'^h\d$')
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._markdown = ''
        self._isP = False
        self._aHref = None
        self._atitle = ''
        self._showunhandled = False
        self._inBody = False
        self._tableCols = 0
        self._inTableCell = False
        self._listLevel = -1
        self._inBlockquote = False
        self._inPre = False
        self._inCode = False
        self._inTh = False

    def handle_starttag(self, tag: str, attrs):
        if tag == 'body':
            self._inBody = True
            return
        if not self._inBody:
            return

        if tag in ['img', 'image', 'div', 'svg', 'tbody']:
            pass
        elif tag == 'p':
            self._isP = True
        elif len(tag) == 2 and tag[0] == 'h' and tag[1].isdigit():
            self._markdown += '\n\n' + '#'*int(tag[1]) + ' '
        elif tag == 'a':
            if type(attrs) == list:
                for key, val in attrs:
                    if key == 'href':
                        self._aHref = val
                        break
            else:
                self._aHref = attrs['href']
        elif tag == 'br':
            self._markdown += '\\\n'
        elif tag == 'em' or tag == 'i':
            self._markdown += '*'
        elif tag == 'strong' or tag == 'b':
            self._markdown += '**'
        elif tag == 'table':
            self._markdown += '\n'
        elif tag == 'tr':
            self._tableCols = 0
        elif tag == 'td':
            self._inTableCell = True
        elif tag == 'th':
            self._inTh = True
            self._inTableCell = True
        elif self._headerRegex.match(tag):
            self._markdown += '#'*int(tag[1]) + ' '
        elif tag == 'span':
            self._markdown += '\n\n'
        elif tag in ['ul', 'ol']:
            self._listLevel += 1
        elif tag == 'li':
            self._markdown += '  '*self._listLevel + '- '
        elif tag == 'blockquote':
            self._inBlockquote = True
            self._markdown += '\n> '
        elif tag == 'pre':
            self._inPre = True
            self._markdown += '\n```\n'
        elif tag == 'code':
            if not self._inPre:
                self._inCode = True
                self._markdown += '`'
        elif tag in ['dl', 'dt', 'dd', 'col', 'colgroup']:
            pass
        elif self._showunhandled:
            sys.stderr.write('STARTTAG> {0}\n'.format(tag))

    def handle_endtag(self, tag):
        if tag == 'body':
            self._inBody = False
        if not self._inBody:
            return

        if tag in ['br', 'img', 'image', 'div', 'svg', 'tbody', 'thead']:
            pass
        elif tag == 'p':
            self._isP = False
            self._markdown += '\n'
        elif tag == 'a':
            if self._aHref and self._aHref.find('.xhtml') == -1:
                self._markdown += '[{0}]({1})'.format(self._atitle, self._aHref)
            elif self._atitle.strip():
                self._markdown += '"{0}"'.format(self._atitle)
            self._atitle = ''
            self._aHref = None
        elif tag == 'em' or tag == 'i':
            self._markdown += '*'
        elif tag == 'strong' or tag == 'b':
            self._markdown += '**'
        elif tag == 'table':
            self._markdown += '\n'
        elif tag == 'thead':
            self._markdown += ' | '.join([' --- ']*self._tableCols).strip() + '\n'
        elif tag == 'td':
            self._inTableCell = False
            self._markdown += ' | '
        elif tag == 'th':
            self._inTh = False
            self._inTableCell = False
            self._markdown += ' | '
        elif tag == 'tr':
            if self._markdown.endswith(' | '):
                self._markdown = self._markdown[:-len(' | ')]
            self._markdown += '\n\n'
        elif self._headerRegex.match(tag):
            self._markdown += '\n'
        elif tag == 'span':
            self._markdown += '\n\n'
        elif tag in ['ul', 'ol']:
            self._listLevel -= 1
        elif tag == 'li':
            self._markdown += '\n'
        elif tag == 'blockquote':
            self._inBlockquote = False
            self._markdown += '\n\n'
        elif tag == 'pre':
            self._inPre = False
            self._markdown += '\n```\n\n'
        elif tag == 'code':
            if not self._inPre and self._inCode:
                self._inCode = False
                self._markdown += '`'
        elif tag in ['dl', 'dt', 'dd', 'col', 'colgroup']:
            pass
        elif self._showunhandled:
            sys.stderr.write('ENDTAG> {0}\n'.format(tag))
        
        if self._markdown.find('.xhtml') != -1:
            raise Exception(tag)

    def handle_data(self, data):
        if not self._inBody:
            return
        data = data.strip()
        if not data:
            return

        if self._aHref != None:
            self._atitle += data
        elif self._inPre:
            self._markdown += data
        elif self._inBlockquote:
            lines = data.split('\n')
            for i, line in enumerate(lines):
                if i > 0:
                    self._markdown += '\n> '
                self._markdown += line
        elif (self._isP or self._inTableCell) and data:
            self._markdown += data + '\n'
        else:
            self._markdown += data
    
    def markdown(self):
        return self._markdown

class Epub:
    NS = {
        "DAISY": "http://www.daisy.org/z3986/2005/ncx/",
        "OPF": "http://www.idpf.org/2007/opf",
        "CONT": "urn:oasis:names:tc:opendocument:xmlns:container",
        "XHTML": "http://www.w3.org/1999/xhtml",
        "EPUB": "http://www.idpf.org/2007/ops"
    }

    def __init__(self, fileepub):
        self.path = os.path.abspath(fileepub)
        self.file = zipfile.ZipFile(fileepub, "r")
        cont = ET.parse(self.file.open("META-INF/container.xml"))
        self.rootfile = cont.find(
            "CONT:rootfiles/CONT:rootfile",
            self.NS
        ).attrib["full-path"]
        self.rootdir = os.path.dirname(self.rootfile)\
            + "/" if os.path.dirname(self.rootfile) != "" else ""
        cont = ET.parse(self.file.open(self.rootfile))
        # EPUB3
        self.version = cont.getroot().get("version")
        if self.version == "2.0":
            # self.toc = self.rootdir + cont.find("OPF:manifest/*[@id='ncx']", self.NS).get("href")
            self.toc = self.rootdir\
                + cont.find(
                    "OPF:manifest/*[@media-type='application/x-dtbncx+xml']",
                    self.NS
                ).get("href")
        elif self.version == "3.0":
            self.toc = self.rootdir\
                + cont.find(
                    "OPF:manifest/*[@properties='nav']",
                    self.NS
                ).get("href")

        self.contents = []
        self.toc_entries = []

    def get_meta(self):
        meta = []
        # why self.file.read(self.rootfile) problematic
        cont = ET.fromstring(self.file.open(self.rootfile).read())
        for i in cont.findall("OPF:metadata/*", self.NS):
            if i.text is not None:
                meta.append([re.sub("{.*?}", "", i.tag), i.text])
        return meta

    def initialize(self):
        cont = ET.parse(self.file.open(self.rootfile)).getroot()
        manifest = []
        for i in cont.findall("OPF:manifest/*", self.NS):
            # EPUB3
            # if i.get("id") != "ncx" and i.get("properties") != "nav":
            if i.get("media-type") != "application/x-dtbncx+xml"\
               and i.get("properties") != "nav":
                manifest.append([
                    i.get("id"),
                    i.get("href")
                ])

        spine, contents = [], []
        for i in cont.findall("OPF:spine/*", self.NS):
            spine.append(i.get("idref"))
        for i in spine:
            for j in manifest:
                if i == j[0]:
                    self.contents.append(self.rootdir+unquote(j[1]))
                    contents.append(unquote(j[1]))
                    manifest.remove(j)
                    # TODO: test is break necessary
                    break

        toc = ET.parse(self.file.open(self.toc)).getroot()
        # EPUB3
        if self.version == "2.0":
            navPoints = toc.findall("DAISY:navMap//DAISY:navPoint", self.NS)
        elif self.version == "3.0":
            navPoints = toc.findall(
                "XHTML:body//XHTML:nav[@EPUB:type='toc']//XHTML:a",
                self.NS
            )
        for i in contents:
            name = "-"
            for j in navPoints:
                # EPUB3
                if self.version == "2.0":
                    # if i == unquote(j.find("DAISY:content", self.NS).get("src")):
                    if re.search(i, unquote(j.find("DAISY:content", self.NS).get("src"))) is not None:
                        name = j.find("DAISY:navLabel/DAISY:text", self.NS).text
                        break
                elif self.version == "3.0":
                    # if i == unquote(j.get("href")):
                    if re.search(i, unquote(j.get("href"))) is not None:
                        name = "".join(list(j.itertext()))
                        break
            self.toc_entries.append(name)


class HTMLtoLines(HTMLParser):
    para = {"p", "div"}
    inde = {"q", "dt", "dd", "blockquote"}
    pref = {"pre"}
    bull = {"li"}
    hide = {"script", "style", "head"}
    # hide = {"script", "style", "head", ", "sub}

    def __init__(self):
        HTMLParser.__init__(self)
        self.text = [""]
        self.imgs = []
        self.ishead = False
        self.isinde = False
        self.isbull = False
        self.ispref = False
        self.ishidden = False
        self.idhead = set()
        self.idinde = set()
        self.idbull = set()
        self.idpref = set()

    def handle_starttag(self, tag, attrs):
        if re.match("h[1-6]", tag) is not None:
            self.ishead = True
        elif tag in self.inde:
            self.isinde = True
        elif tag in self.pref:
            self.ispref = True
        elif tag in self.bull:
            self.isbull = True
        elif tag in self.hide:
            self.ishidden = True
        elif tag == "sup":
            self.text[-1] += "^{"
        elif tag == "sub":
            self.text[-1] += "_{"
        # NOTE: "img" and "image"
        # In HTML, both are startendtag (no need endtag)
        # but in XHTML both need endtag
        elif tag in {"img", "image"}:
            for i in attrs:
                if (tag == "img" and i[0] == "src")\
                   or (tag == "image" and i[0].endswith("href")):
                    self.text.append("[IMG:{}]".format(len(self.imgs)))
                    self.imgs.append(unquote(i[1]))

    def handle_startendtag(self, tag, attrs):
        if tag == "br":
            self.text += [""]
        elif tag in {"img", "image"}:
            for i in attrs:
                if (tag == "img" and i[0] == "src")\
                   or (tag == "image" and i[0].endswith("href")):
                    self.text.append("[IMG:{}]".format(len(self.imgs)))
                    self.imgs.append(unquote(i[1]))
                    self.text.append("")

    def handle_endtag(self, tag):
        if re.match("h[1-6]", tag) is not None:
            self.text.append("")
            self.text.append("")
            self.ishead = False
        elif tag in self.para:
            self.text.append("")
        elif tag in self.hide:
            self.ishidden = False
        elif tag in self.inde:
            if self.text[-1] != "":
                self.text.append("")
            self.isinde = False
        elif tag in self.pref:
            if self.text[-1] != "":
                self.text.append("")
            self.ispref = False
        elif tag in self.bull:
            if self.text[-1] != "":
                self.text.append("")
            self.isbull = False
        elif tag in {"sub", "sup"}:
            self.text[-1] += "}"
        elif tag in {"img", "image"}:
            self.text.append("")

    def handle_data(self, raw):
        if raw and not self.ishidden:
            if self.text[-1] == "":
                tmp = raw.lstrip()
            else:
                tmp = raw
            if self.ispref:
                line = unescape(tmp)
            else:
                line = unescape(re.sub(r"\s+", " ", tmp))
            self.text[-1] += line
            if self.ishead:
                self.idhead.add(len(self.text)-1)
            elif self.isbull:
                self.idbull.add(len(self.text)-1)
            elif self.isinde:
                self.idinde.add(len(self.text)-1)
            elif self.ispref:
                self.idpref.add(len(self.text)-1)

    def get_lines(self, width=0):
        text = []
        if width == 0:
            return self.text
        for n, i in enumerate(self.text):
            if n in self.idhead:
                text += [i.rjust(width//2 + len(i)//2)] + [""]
            elif n in self.idinde:
                text += ["   "+j for j in textwrap.wrap(i, width - 3)] + [""]
            elif n in self.idbull:
                tmp = textwrap.wrap(i, width - 3)
                text += [" - "+j if j == tmp[0] else "   "+j for j in tmp] + [""]
            elif n in self.idpref:
                tmp = i.splitlines()
                wraptmp = []
                for line in tmp:
                    wraptmp += [j for j in textwrap.wrap(line, width - 6)]
                text += ["   "+j for j in wraptmp] + [""]
            else:
                text += textwrap.wrap(i, width) + [""]
        return text, self.imgs