# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 10:41:33 2018

@author: Shivank.r
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 15:30:42 2018

@author: Shivank.r
"""
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
import re
import itertools
import os
import subprocess
from docx.opc.constants import RELATIONSHIP_TYPE as RT

def file_converter(path):
    iowriter = "/usr/bin/libreoffice"
    if path.endswith('.docx'):
        return (path,"doc")
    abspath = os.path.normpath(path)
    outdir = os.path.dirname(abspath)  
    if path.endswith('.pdf'):
        return (path,"pdf")
    elif path.endswith('.doc'):
        x = '"' + iowriter+ '"' +' --convert-to docx --outdir ' + '"' + outdir + '" ' + '"' + abspath + '"'
        subprocess.call(x, shell=True)
    elif path.endswith('.odt'):
        x = '"' + iowriter+ '"' +' --convert-to docx --outdir ' + '"' + outdir + '" ' + '"' + abspath + '"'
        subprocess.call(x, shell=True)
    elif path.endswith('.rtf'):
        x = '"' + iowriter+ '"' +' --convert-to docx --outdir ' + '"' + outdir + '" ' + '"' + abspath + '"'
        subprocess.call(x, shell=True)   
    return (path[:-3] + 'docx',"doc")


def iter_block_items(parent):
    """
    Generate a reference to each paragraph and table child within *parent*,
    in document order. Each returned value is an instance of either Table or
    Paragraph. *parent* would most commonly be a reference to a main
    Document object, but also works for a _Cell object, which itself can
    contain paragraphs and tables.
    """
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
        # print(parent_elm.xml)
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)
            
def items(document):
    array=[]
    for block in iter_block_items(document):
        array.append(block)
    return array
def iter_hyperlink_rels(rels):
    for rel in rels.keys():
        if rels[rel].reltype == RT.HYPERLINK and "mailto:" in rels[rel]._target:
            yield rel

    
def text_to_convert(table):
    list_rows = []
    for i in table.rows:    
        list_cells = []
        for q in i.cells:
            item_cells = items(q)
            for i in item_cells:
                if isinstance(i,Paragraph) and i.text.strip()=="":
                    item_cells.remove(i)
            string  = docs_conversion(item_cells)
            list_cells.append(string)
        list_rows.append('\t'.join(list_cells))
    return '\n'.join(list_rows)
        

def docs_conversion(docs):
    temp = []
    for i in docs:
        if isinstance(i,Paragraph):
            temp.append(i.text.strip())
        if isinstance(i,Table):
            temp.append(text_to_convert(i))
            
    return '\n'.join(temp)

def relations(resume_string):
    result=[]
    strings=resume_string.split("\n")
    for i in strings:
        t=re.findall("((?:[A-z][A-z\s\’\-\.]+)(?::-|:|\t+)(?:[\s]*(?:[\w\\\/\-\\@+\'\.\,\(\)]+[ ]?)+ ?))",i)
        if t:
           result.append(t)
    result=list(itertools.chain.from_iterable(result))
    result=list(map(lambda x: x.split(":-")if ":-" in x else (x.split(":") if ":" in x else x.split("\t")),result))
    result=list(filter(lambda x: len(x)==2,result))
    return result
    
