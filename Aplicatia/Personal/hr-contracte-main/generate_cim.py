#!/usr/bin/env python3
# generate_cim.py - Generator CIM cu python-docx
# Instalare: pip install python-docx
# Utilizare: python generate_cim.py '{"prenume":"Ion","nume":"Popescu",...}'

import sys
import json
import io
from datetime import datetime

try:
    from docx import Document
except ImportError:
    print("ERROR: python-docx not installed. Run: pip install python-docx", file=sys.stderr)
    sys.exit(1)

def fmt_date(d):
    if not d:
        return '___________'
    try:
        dt = datetime.fromisoformat(str(d).replace('Z',''))
        return dt.strftime('%d.%m.%Y')
    except:
        return str(d)

def v(x):
    return str(x) if x else '___________'

def replace_in_para(para, old, new):
    run_texts = [r.text for r in para.runs]
    combined = ''.join(run_texts)
    if old not in combined:
        return False
    new_combined = combined.replace(old, new, 1)
    if para.runs:
        para.runs[0].text = new_combined
        for r in para.runs[1:]:
            r.text = ''
    return True

def replace_all(doc, replacements):
    for para in doc.paragraphs:
        for old, new in replacements:
            replace_in_para(para, old, new)

def generate_cim(data):
    import os
    model_path = os.path.join(os.path.dirname(__file__), 'model_cim.docx')
    doc = Document(model_path)
    
    azi = datetime.now().strftime('%d.%m.%Y')
    data_contract = fmt_date(data.get('data_contract')) if data.get('data_contract') else azi
    data_angajare = fmt_date(data.get('data_angajare'))
    data_ci = fmt_date(data.get('ci_data'))
    nr_revisal = v(data.get('nr_revisal', '___'))
    
    prenume = v(data.get('prenume'))
    nume = v(data.get('nume'))
    nume_complet = (prenume + ' ' + nume).upper()
    
    domiciliu = v(data.get('domiciliu'))
    # Separăm domiciliul în localitate și stradă
    dom_parts = domiciliu.split(',')
    localitate = dom_parts[0].strip().upper() if dom_parts else domiciliu.upper()
    strada = ','.join(dom_parts[1:]).strip() if len(dom_parts) > 1 else 'STR. ___'
    
    ci_serie_nr = v(data.get('ci_serie_nr'))
    ci_parts = ci_serie_nr.split(' ')
    ci_nr = ''.join(ci_parts[1:]) if len(ci_parts) > 1 else ci_serie_nr
    
    ci_elib = v(data.get('ci_eliberat_de')).upper()
    
    salariu = str(int(float(data['salariu']))) if data.get('salariu') else '___________'
    functie = v(data.get('functie'))
    
    replacements = [
        ('MICHI NELU-CLAUDIU', nume_complet),
        ('CLUJ NAPOCA', localitate),
        ('LIPSA DOMICILIU', strada),
        ('358880', ci_nr),
        ('SPCLEP CLUJ', ci_elib),
        ('10.11.2025', data_ci),
        ('1960728125822', v(data.get('cnp'))),
        ('06.05.2026', data_contract),
        ('07.05.2026', data_angajare),
        ('232', nr_revisal),
        ('4582', salariu),
        ('MUNCITOR NECALIFICAT la demolarea cladirilor, captuseli, zidarie, placi mozaic, faianta, gresie, parchet cod COR 931301', functie),
    ]
    
    replace_all(doc, replacements)
    
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generate_cim.py '<json_data>'", file=sys.stderr)
        sys.exit(1)
    
    data = json.loads(sys.argv[1])
    result = generate_cim(data)
    sys.stdout.buffer.write(result)
