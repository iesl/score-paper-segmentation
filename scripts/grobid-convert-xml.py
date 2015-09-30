import os
from nltk import metrics
import re
import sys
from lxml import etree
import codecs


def proc_grobid(fname):
    parser = etree.XMLParser(encoding = 'iso-8859-1')
    root = etree.parse(fname, parser = parser).getroot()
    uri = '{http://www.tei-c.org/ns/1.0}'
    header = root.find(uri+'teiHeader')
    top = header.find(uri+'fileDesc')

    def printTree(node):
        '''helper function to print xml text tree starting from a root'''
        if not node.getchildren( ): return node.text.strip() if node.text else ""
        return (node.text.strip() + " " if node.text else "") + " ".join(map(printTree, node.getchildren()))

    # output header string
    header_str = ""
    # find title, author info (names, affiliation, addr, email) and abstract 
    title = top.find(uri+'titleStmt').find(uri+'title').text
    if title: title = title.strip()
    else: title = ""

    auth_infs = []
    for auth in header.iter(uri+'author'):
        auth_infs.append(printTree(auth).strip())

    abstract = "Abstract\n"
    abs_node = header.find(uri+'profileDesc').find(uri+'abstract')
    abstract += printTree(abs_node)

    header_str += title + "\n" + "\n".join(auth_infs) + "\n" + abstract + "\n"

    def printRefs(bibl):
        ''' helper function to print out each reference in the format:
            Authors. Year. Title. Proceedings(, Vol. #)(, pages #-#.)'''
        authors = []
        for auth in bibl.iter(uri+'persName'):
            name = ""
            for first in auth.iter(uri+'forename'):
                if first.text:
                    fname = first.text.strip()
                    if len(fname) == 1: fname += "."
                    name += fname + " "
            for last in auth.iter(uri+'surname'):
                if last.text:
                    surname = last.text.strip()
                    name = name.strip() + " " + surname
            authors.append(name)
        auth_inf = ', '.join(authors)
        year = " ".join([x.attrib['when'] for x in bibl.iter(uri+'date') if 'when' in x.attrib])
        title = " ".join([x.text.strip() for x in bibl.iter(uri+'title') if 'type' in x.attrib and x.attrib['type'] == 'main'])
        proc = " ".join([x.text.strip() for x in bibl.iter(uri+'title') if x.text and ('type' not in x.attrib or
                                                                                       x.attrib['type'] != 'main')])
        vol_elem = "".join([x.text.strip() for x in bibl.iter(uri+'biblScope') if 'unit' in x.attrib and x.attrib['unit'] == 'volume'])
        vol = ""
        if len(vol_elem) > 0: vol = "Vol. " + vol_elem.strip()
        
        pages_elem = [(x.attrib['from'],x.attrib['to']) for x in bibl.iter(uri+'biblScope') if 'unit' in x.attrib and x.attrib['unit'] == 'page' and 'from' in x.attrib]
        pages = ""
        if len(pages_elem) > 0: pages = "pages " + pages_elem[0][0]+"-"+pages_elem[0][1]

        toInc  = lambda x: x.strip() + ". " if x.strip() != "" else ""

        ref = "" + toInc(auth_inf) + toInc(year) + toInc(title)
        if proc.strip():
            ref += proc.strip()
            if vol.strip(): ref += ", " + vol.strip()
            if pages.strip(): ref += ", " + pages.strip()
        
        ref = ref.strip()
        if ref[-1] != ".": ref += "."
        return ref


    # find reference text
    refs = root.find(uri+'text').find(uri+'back').find(uri+"div[@type='references']").find(uri+'listBibl')
    references = "References\n" + "\n". join(map(printRefs, refs.findall(uri+'biblStruct')))

    return "#Header\n"+ header_str + "#Body\n IGNORE\n" + "#References\n" + references

def proc_rpp_anno(fname, type = 'anno'):
    ''' If type == 'rpp':
        Extract header and reference from RPP output
        Header begins with token "#Header" and runs till token "#References"
        Referenes begin with token "#References" till end of file
        If type = 'anno':
        Extract the header and references from ground truth.
        Format is same as RPP, with the only difference that the section titles
        are already present in the text'''
    with open(fname, 'r') as f:
        in_str = f.read()
    
    if type == 'anno': head_pattern = re.compile(r'#Header(.*)#Body', re.S)
    else: head_pattern = re.compile(r'#Header(.*)#References', re.S)
    ref_pattern = re.compile(r'#References(.*)\Z', re.S)
    header = re.search(head_pattern, in_str).group(1)
    refs = re.search(ref_pattern, in_str).group(1)

    if type == 'rpp': return header, "References\n" + refs
    return header, refs

def sanitizer(instr):
    ''' Clean input string by discarding all line breaks and replacing by a
        whitespace. Replace multiple whitespaces by single'''
    out = re.sub('\n', ' ', instr)
    return re.sub(r'[\s]+', ' ', out)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'Usage: python grobid-convert-xml.py grobid-folder output-folder'
        sys.exit()
    gfolder = sys.argv[1]
    fnames = filter(lambda x: len(re.findall('xml', x)) > 0, os.listdir(gfolder))
    outfolder = sys.argv[2].strip()
    if not os.path.exists(outfolder): os.mkdir(outfolder)
    print "Num files to process:", len(fnames)
    for f in fnames:
        procout = proc_grobid(gfolder + "/"+ f)
        with codecs.open(outfolder + "/" + f, mode = "w+", encoding = "iso-8859-1") as outf:
            outf.write(procout)
        print f