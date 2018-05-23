import xml.etree.ElementTree as ET
import subprocess
import os

def parse_pdfs(input_folder, 
               output_folder, 
               grobid_path='~/grobid-0.5.1', 
               grobid_version='0.5.1', 
               is_recursive=True):
    grobid_core_path = os.path.join(grobid_path, 'grobid-core', 'build', 'libs', 'grobid-core-' + grobid_version + '-onejar.jar')
    grobid_home_path = os.path.join(grobid_path, 'grobid-home')
    recursive_mod = ' -r ' if is_recursive else ' '
    cmd_prefix = 'java -Xmx1G -jar ' + grobid_core_path + ' -gH ' + grobid_home_path + ' -dIn ' + input_folder + ' -dOut ' + output_folder + recursive_mod + '-exe '
    process_header_output = subprocess.check_output(cmd_prefix + 'processHeader', shell=True)
    process_references_output = subprocess.check_output(cmd_prefix + 'processReferences', shell=True)

# this method is likely a stub
def extract_metadata(v, result, mode = None, print_tree = False, indent = 0):
    tag = v.tag.split('}')[1]
    if print_tree:
        print('-'*indent + ' ' + tag, end = '')
    if tag == 'title' or tag == 'date' or mode == 'abstract':
        if mode is None:
            mode = tag
        if v.text is not None:
            result[mode] = v.text
            if print_tree:
                print(': ' + v.text)
    else:
        if print_tree:
            print('')
    for c in v.getchildren():
        m = tag if tag == 'abstract' else None            
        extract_metadata(c, result, m, print_tree, indent + 1)

# this method is likely a stub
def extract_references(v, result, mode = None):
    tag = v.tag.split('}')[1]
    if tag == 'title':
        if v.text is not None:
            result[-1][mode][tag] = v.text
        else:
            if tag not in result[-1][mode]:
                result[-1][mode][tag] = '<None>'
    if tag == 'date':
        result[-1][mode][tag] = v.attrib['when']
        
    m = None
    if tag == 'biblStruct':
        result.append({})
        m = tag
    if tag == 'analytic' or tag == 'monogr':
        result[-1][tag] = {}
        m = tag
    
    if m is None:
        m = mode
    for c in v.getchildren():
        extract_references(c, result, m)

# this method is likely a stub
def process_refs(refs):
    prefs = []
    for ref in refs:
        pref = {}
        if 'analytic' in ref and 'monogr' in ref:   
            if 'title' in ref['analytic']: 
                pref['title'] = ref['analytic']['title']
            elif 'title' in ref['monogr']:
                pref['title'] = ref['monogr']['title']
            else:
                pref['title'] = 'None'
            if 'date' in ref['monogr']:
                pref['date'] = ref['monogr']['date']
        elif 'analytic' in ref:
            pref = ref['analytic']
        elif 'monogr' in ref:
            pref = ref['monogr']
        
        prefs.append(pref)
    return prefs

def get_paper_metadata(path):
    tree = ET.parse(path)
    root = tree.getroot()
    metadata = {}
    extract_metadata(root, metadata)
    return metadata

def get_paper_references(path):
    tree = ET.parse(path)
    root = tree.getroot()
    references = []
    extract_references(root, references)
    return process_refs(references)