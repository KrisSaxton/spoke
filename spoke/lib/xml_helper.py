"""XML helper modules

Classes:
None

Exceptions:
SpokeError - raised when action fails for unknown reason.
"""
# core modules
from xml.dom.minidom import Document
import StringIO

# own modules
import spoke.lib.error as error

try:
    import xml.etree.ElementTree as ET # needs python =>2.5
except:
    msg = 'Failed to import xml.etree.ElementTree, is your python => 2.5?'
    raise error.SpokeError(msg)

def createDoc(doc_name):
    doc_name = Document()
    return doc_name

def createElement(doc_name, element, attribute=None):
    element = doc_name.createElement(element)
    if (attribute is not None):
        for key in attribute:
            value = attribute[key]
            element.setAttribute(key, value)        
    doc_name.appendChild(element)
    return element
    
def createChild(doc_name, parent, element, attribute=None, content=None):
    element = doc_name.createElement(element)
    if (attribute is not None):
        for key in attribute:
            value = attribute[key]
            element.setAttribute(key, value)
    if (content is not None):
        content = doc_name.createTextNode(content)
        element.appendChild(content)
    parent.appendChild(element)
    return element

def _get_max_width(data, index):
    """Gets the max width for any column (index) in list (data)"""
    return max([len(data[i][index]) for i in range(0, len(data))])
    
def xml_to_text(xml_list, headers):
    """Extract elements from an xml document as specified (headers) and print 
    them as a nicely formatted table, padded for alignment. 
    Each row must have the same number of columns. """
    result = []
    result.append(headers)
    for doc in xml_list:
        element = ET.fromstring(doc)
        entry = []
        for header in headers:
            entry.append(element.findtext(header))
        result.append(entry)
    
    out = StringIO.StringIO()
    col_paddings = []
    # Built a list of max column lengths
    for i in range(len(result[0])):
        col_paddings.append(_get_max_width(result, i))
    # Print as table with padding as per max column lengths
    for row in result:
        # left column
        print >> out, row[0].ljust(col_paddings[0] + 1),
        # remaining columns
        for i in range(1, len(row)):
            col = row[i].ljust(col_paddings[i] + 1)
            print >> out, col,
        print >> out
    data = out.getvalue()
    out.close()
    return data
    
def out(doc_name):
    return doc_name.toxml()
