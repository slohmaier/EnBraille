import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tempfile
import zipfile
import os
import sys
import xml.etree.ElementTree as etree
from unittest.mock import Mock, MagicMock
from io import BytesIO

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util_epub import epub2md, MDFilter, Epub
from enbraille_functions.document import EnBrailleMd2BRF
from enbraille_data import EnBrailleData
from PySide6.QtGui import QGuiApplication

def get_shared_app():
    """Get or create shared QGuiApplication instance"""
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication([])
    return app

def gen_test_data() -> EnBrailleData:
    """Generate test data without creating new QApplication"""
    app = get_shared_app()
    data = EnBrailleData(app)
    return data


class TestMDFilter(unittest.TestCase):
    """Test the MDFilter HTML parser for paragraph and content parsing"""
    
    def setUp(self):
        self.filter = MDFilter()
    
    def test_simple_paragraph(self):
        """Test parsing of simple paragraph"""
        html = "<body><p>This is a simple paragraph.</p></body>"
        self.filter.feed(html)
        self.filter.close()
        result = self.filter.markdown()
        self.assertIn("This is a simple paragraph.", result)
    
    def test_paragraph_with_emphasis(self):
        """Test paragraph with emphasis and strong tags"""
        html = "<body><p>This is <em>emphasized</em> and <strong>strong</strong> text.</p></body>"
        self.filter.feed(html)
        self.filter.close()
        result = self.filter.markdown()
        # Check that emphasis and strong markers are present
        self.assertIn("*emphasized", result)
        self.assertIn("**strong", result)
        self.assertIn("emphasized", result)
        self.assertIn("strong", result)
    
    def test_paragraph_with_line_break(self):
        """Test paragraph with line breaks"""
        html = "<body><p>First line<br/>Second line</p></body>"
        self.filter.feed(html)
        self.filter.close()
        result = self.filter.markdown()
        self.assertIn("\\\n", result)
    
    def test_headings(self):
        """Test various heading levels"""
        for level in range(1, 7):
            with self.subTest(level=level):
                filter = MDFilter()
                html = f"<body><h{level}>Heading Level {level}</h{level}></body>"
                filter.feed(html)
                filter.close()
                result = filter.markdown()
                expected_hashes = '#' * level
                self.assertIn(expected_hashes, result)
                self.assertIn(f"Heading Level {level}", result)
    
    def test_lists(self):
        """Test unordered and ordered lists"""
        html = """<body>
        <ul>
            <li>First item</li>
            <li>Second item</li>
        </ul>
        <ol>
            <li>First numbered</li>
            <li>Second numbered</li>
        </ol>
        </body>"""
        self.filter.feed(html)
        self.filter.close()
        result = self.filter.markdown()
        self.assertIn("- First item", result)
        self.assertIn("- Second item", result)
    
    def test_links(self):
        """Test link parsing"""
        html = '<body><a href="https://example.com">Example Link</a></body>'
        self.filter.feed(html)
        self.filter.close()
        result = self.filter.markdown()
        self.assertIn("[Example Link](https://example.com)", result)
    
    def test_blockquote(self):
        """Test blockquote parsing"""
        html = "<body><blockquote>This is a quote</blockquote></body>"
        self.filter.feed(html)
        self.filter.close()
        result = self.filter.markdown()
        self.assertIn("> This is a quote", result)
    
    def test_code_blocks(self):
        """Test code and pre blocks"""
        html = "<body><pre>code block</pre><code>inline code</code></body>"
        self.filter.feed(html)
        self.filter.close()
        result = self.filter.markdown()
        self.assertIn("```", result)
        self.assertIn("`inline code`", result)
    
    def test_table(self):
        """Test table parsing"""
        html = """<body>
        <table>
            <thead>
                <tr><th>Header 1</th><th>Header 2</th></tr>
            </thead>
            <tbody>
                <tr><td>Cell 1</td><td>Cell 2</td></tr>
            </tbody>
        </table>
        </body>"""
        self.filter.feed(html)
        self.filter.close()
        result = self.filter.markdown()
        # Check that table elements are present in some form
        self.assertIn("Header 1", result)
        self.assertIn("Header 2", result)
        self.assertIn("Cell 1", result)
        self.assertIn("Cell 2", result)
        self.assertIn("|", result)


class TestEpub2Md(unittest.TestCase):
    """Test the epub2md function"""
    
    def create_test_epub(self):
        """Create a minimal test EPUB file"""
        # Create temporary file
        epub_file = tempfile.NamedTemporaryFile(suffix='.epub', delete=False)
        
        # Create ZIP structure for EPUB
        with zipfile.ZipFile(epub_file.name, 'w') as epub:
            # Add mimetype
            epub.writestr('mimetype', 'application/epub+zip')
            
            # Add META-INF/container.xml
            container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
            <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
                <rootfiles>
                    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
                </rootfiles>
            </container>'''
            epub.writestr('META-INF/container.xml', container_xml)
            
            # Add content.opf
            content_opf = '''<?xml version="1.0" encoding="UTF-8"?>
            <package version="2.0" xmlns="http://www.idpf.org/2007/opf">
                <metadata>
                    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Test Book</dc:title>
                </metadata>
                <manifest>
                    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
                    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
                </manifest>
                <spine toc="ncx">
                    <itemref idref="chapter1"/>
                </spine>
            </package>'''
            epub.writestr('OEBPS/content.opf', content_opf)
            
            # Add toc.ncx
            toc_ncx = '''<?xml version="1.0" encoding="UTF-8"?>
            <ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
                <head>
                    <meta name="dtb:uid" content="test"/>
                </head>
                <docTitle><text>Test Book</text></docTitle>
                <navMap>
                    <navPoint id="chapter1">
                        <navLabel><text>Chapter 1</text></navLabel>
                        <content src="chapter1.xhtml"/>
                    </navPoint>
                </navMap>
            </ncx>'''
            epub.writestr('OEBPS/toc.ncx', toc_ncx)
            
            # Add chapter1.xhtml
            chapter_html = '''<?xml version="1.0" encoding="UTF-8"?>
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head><title>Chapter 1</title></head>
            <body>
                <h1>Chapter One</h1>
                <p>This is the first paragraph with <em>emphasis</em>.</p>
                <p>This is the second paragraph with <strong>bold</strong> text.</p>
                <ul>
                    <li>First item</li>
                    <li>Second item</li>
                </ul>
            </body>
            </html>'''
            epub.writestr('OEBPS/chapter1.xhtml', chapter_html)
        
        return epub_file.name
    
    def test_epub2md_conversion(self):
        """Test conversion of EPUB to Markdown"""
        epub_path = self.create_test_epub()
        try:
            result = epub2md(epub_path)
            
            # Check that we get markdown content
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            
            # Check for expected content
            self.assertIn("Chapter One", result)
            self.assertIn("first paragraph", result)
            self.assertIn("emphasis", result)
            self.assertIn("bold", result)
            self.assertIn("First item", result)
            
        finally:
            # Clean up
            os.unlink(epub_path)
    
    def test_epub_class_initialization(self):
        """Test Epub class initialization"""
        epub_path = self.create_test_epub()
        try:
            epub = Epub(epub_path)
            epub.initialize()
            
            # Check that contents were loaded
            self.assertGreater(len(epub.contents), 0)
            self.assertIn('chapter1.xhtml', epub.contents[0])
            
        finally:
            os.unlink(epub_path)


class TestEnBrailleMd2BRF(unittest.TestCase):
    """Test the EnBrailleMd2BRF class"""
    
    def setUp(self):
        self.data = gen_test_data()
        # Set up test data
        self.data.documentTable = 'en-us-g1.ctb'
        self.data.documentLineLength = 40
        self.data.documentH1Char = '='
        self.data.documentH2Char = '-'
        self.data.documentH3Char = '*'
        self.data.documentH4Char = '+'
        self.data.documentH5Char = '~'
        self.data.documentH6Char = '^'
        self.data.documentBulletL1Char = '•'
        self.data.documentBulletL2Char = '◦'
        self.data.documentBulletL3Char = '▪'
        self.data.documentBulletL4Char = '▫'
        self.data.documentBulletL5Char = '‣'
        self.data.documentBulletL6Char = '⁃'
        
        self.converter = EnBrailleMd2BRF(self.data)
        # Mock the translation function for testing
        self.converter._translate = Mock(side_effect=lambda x: x if x else '')
    
    def create_element(self, tag, text=None, attrib=None):
        """Helper to create XML elements for testing"""
        element = etree.Element(tag, attrib or {})
        if text:
            element.text = text
        return element
    
    def test_convert_paragraph(self):
        """Test paragraph conversion"""
        element = self.create_element('p', 'This is a test paragraph.')
        result = self.converter.convert_paragraph(element)
        self.assertEqual(result, 'This is a test paragraph.\n')
    
    def test_convert_headings(self):
        """Test heading conversion for all levels"""
        for level in range(1, 7):
            with self.subTest(level=level):
                element = self.create_element(f'h{level}', f'Heading {level}')
                result = self.converter.convert_heading(element, level)
                
                # Check that result contains the heading text and has proper structure
                self.assertIn(f'Heading {level}', result)
                # Should have newlines around heading
                self.assertTrue(result.count('\n') >= 2)
                # Should have some translated character at the beginning
                self.assertGreater(len(result.strip()), len(f'Heading {level}'))
    
    def test_convert_emphasis(self):
        """Test emphasis conversion"""
        element = self.create_element('em', 'emphasized text')
        result = self.converter.convert_emphasis(element)
        self.assertEqual(result, '*emphasized text*')
    
    def test_convert_strong(self):
        """Test strong text conversion"""
        element = self.create_element('strong', 'bold text')
        result = self.converter.convert_strong(element)
        self.assertEqual(result, '**bold text**')
    
    def test_convert_code(self):
        """Test code conversion"""
        element = self.create_element('code', 'print("hello")')
        result = self.converter.convert_code(element)
        self.assertEqual(result, '`print("hello")`')
    
    def test_convert_preformatted(self):
        """Test preformatted text conversion"""
        element = self.create_element('pre', 'code block\nline 2')
        result = self.converter.convert_preformatted(element)
        self.assertIn('```', result)
        self.assertIn('code block\nline 2', result)
    
    def test_convert_link(self):
        """Test link conversion"""
        element = self.create_element('a', 'Example', {'href': 'https://example.com'})
        result = self.converter.convert_link(element)
        self.assertEqual(result, 'Example (https://example.com)')
    
    def test_convert_list(self):
        """Test list conversion"""
        # Create unordered list
        ul = self.create_element('ul')
        li1 = self.create_element('li', 'First item')
        li2 = self.create_element('li', 'Second item')
        ul.append(li1)
        ul.append(li2)
        
        result = self.converter.convert_unordered_list(ul)
        self.assertIn('First item', result)
        self.assertIn('Second item', result)
    
    def test_convert_table(self):
        """Test table conversion"""
        # Create table structure
        table = self.create_element('table')
        tr = self.create_element('tr')
        td1 = self.create_element('td', 'Cell 1')
        td2 = self.create_element('td', 'Cell 2')
        tr.append(td1)
        tr.append(td2)
        table.append(tr)
        
        result = self.converter.convert_table(table)
        self.assertIn('Cell 1 | Cell 2', result)
    
    def test_convert_superscript_subscript(self):
        """Test superscript and subscript conversion"""
        sup_elem = self.create_element('sup', '2')
        sub_elem = self.create_element('sub', 'x')
        
        sup_result = self.converter.convert_superscript(sup_elem)
        sub_result = self.converter.convert_subscript(sub_elem)
        
        self.assertEqual(sup_result, '^{2}')
        self.assertEqual(sub_result, '_{x}')
    
    def test_convert_deleted_inserted(self):
        """Test deleted and inserted text conversion"""
        del_elem = self.create_element('del', 'deleted text')
        ins_elem = self.create_element('ins', 'inserted text')
        
        del_result = self.converter.convert_deleted(del_elem)
        ins_result = self.converter.convert_inserted(ins_elem)
        
        self.assertEqual(del_result, '~~deleted text~~')
        self.assertEqual(ins_result, '++inserted text++')
    
    def test_convert_definition_list(self):
        """Test definition list conversion"""
        dt_elem = self.create_element('dt', 'Term')
        dd_elem = self.create_element('dd', 'Definition')
        
        dt_result = self.converter.convert_definition_list_item(dt_elem)
        dd_result = self.converter.convert_definition_list_item(dd_elem)
        
        self.assertEqual(dt_result, '**Term**\n')
        self.assertEqual(dd_result, '  Definition\n')
    
    def test_convert_elements_mixed_content(self):
        """Test conversion of elements with mixed content"""
        # Create paragraph with nested elements
        p = self.create_element('p')
        p.text = 'Start '
        
        em = self.create_element('em', 'emphasized')
        em.tail = ' and '
        p.append(em)
        
        strong = self.create_element('strong', 'bold')
        strong.tail = ' end.'
        p.append(strong)
        
        result = self.converter.convert_elements(p)
        self.assertIn('Start', result)
        self.assertIn('*emphasized*', result)
        self.assertIn('and', result)
        self.assertIn('**bold**', result)
        self.assertIn('end.', result)
    
    def test_horizontal_rule(self):
        """Test horizontal rule conversion"""
        hr = self.create_element('hr')
        result = self.converter.convert_horizontal_rule(hr)
        self.assertIn('-', result)
        self.assertTrue(len(result.strip()) > 0)
    
    def test_line_break(self):
        """Test line break conversion"""
        br = self.create_element('br')
        result = self.converter.convert_line_break(br)
        self.assertEqual(result, '\n')
    
    def test_image_handling(self):
        """Test image element handling"""
        img = self.create_element('img', attrib={'src': 'image.jpg', 'alt': 'Test image'})
        result = self.converter.convert_image(img)
        # Images should return empty string as per current implementation
        self.assertEqual(result, '')


if __name__ == '__main__':
    unittest.main()