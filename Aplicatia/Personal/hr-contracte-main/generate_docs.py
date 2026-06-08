#!/usr/bin/env python3
# generate_docs.py - Generator documente HR
# Utilizare: python generate_docs.py '<tip>' '<json_angajat>'

import sys
import json
import io
import os
import zipfile
from datetime import datetime

try:
    from docx import Document
except ImportError:
    print("ERROR: python-docx not installed", file=sys.stderr)
    sys.exit(1)

BASE_DIR = os.path.dirname(__file__)

def fmt_date(d):
    if not d: return '___________'
    try:
        dt = datetime.fromisoformat(str(d).replace('Z',''))
        return dt.strftime('%d.%m.%Y')
    except:
        return str(d)

def v(x):
    return str(x).strip() if x else '___________'

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
            if old and old in para.text:
                replace_in_para(para, old, new)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for old, new in replacements:
                        if old and old in para.text:
                            replace_in_para(para, old, new)

def to_buffer(doc):
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()

def get_replacements(a):
    azi = datetime.now().strftime('%d.%m.%Y')
    data_angajare = fmt_date(a.get('data_angajare'))
    data_ci = fmt_date(a.get('ci_data'))
    
    prenume = v(a.get('prenume'))
    nume = v(a.get('nume'))
    nume_complet = (prenume + ' ' + nume).upper()
    
    domiciliu = v(a.get('domiciliu'))
    dom_parts = domiciliu.split(',')
    localitate = dom_parts[0].strip().upper() if dom_parts else ''
    strada = dom_parts[1].strip() if len(dom_parts) > 1 else ''
    nr = ''
    judet = dom_parts[-1].strip().upper() if len(dom_parts) > 2 else ''
    
    ci = v(a.get('ci_serie_nr'))
    ci_parts = ci.split(' ')
    ci_serie = ci_parts[0] if ci_parts else ''
    ci_nr = ''.join(ci_parts[1:]) if len(ci_parts) > 1 else ci
    
    cnp = v(a.get('cnp'))
    ci_elib = v(a.get('ci_eliberat_de')).upper()
    salariu = str(int(float(a['salariu']))) if a.get('salariu') else '___'
    functie = v(a.get('functie'))
    nr_contract = v(a.get('nr_contract', '___'))
    nr_revisal = v(a.get('nr_revisal', '___'))
    data_contract = fmt_date(a.get('data_contract')) if a.get('data_contract') else azi
    
    return {
        'azi': azi,
        'data_angajare': data_angajare,
        'data_contract': data_contract,
        'data_ci': data_ci,
        'prenume': prenume,
        'nume': nume,
        'nume_complet': nume_complet,
        'localitate': localitate,
        'strada': strada,
        'judet': judet,
        'ci_serie': ci_serie,
        'ci_nr': ci_nr,
        'ci_elib': ci_elib,
        'cnp': cnp,
        'salariu': salariu,
        'functie': functie,
        'nr_contract': nr_contract,
        'nr_revisal': nr_revisal,
        'data_contract': data_contract,
    }

def xml_replace(model_filename, replacements):
    """Replace text directly in XML - handles fragmented runs."""
    import zipfile, io as _io
    model_path = os.path.join(BASE_DIR, model_filename)
    with open(model_path, 'rb') as f:
        model_bytes = f.read()
    zin = zipfile.ZipFile(_io.BytesIO(model_bytes))
    zout_buf = _io.BytesIO()
    with zipfile.ZipFile(zout_buf, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'word/document.xml':
                xml = data.decode('utf-8')
                for old, new in replacements:
                    if old:
                        xml = xml.replace(old, new)
                data = xml.encode('utf-8')
            zout.writestr(item, data)
    zout_buf.seek(0)
    return zout_buf.read()


# ── GENERATOARE ───────────────────────────────────────────────────────────────

def gen_fisa_post(a):
    r = get_replacements(a)
    return xml_replace('model_fisa_post.docx', [
        ('DANI ALIN', r['nume_complet']),
        ('243/26.05.2026', r['nr_contract'] + '/' + r['data_contract']),
        ('26.05.2026', r['data_contract']),
    ])

def gen_regulament(a):
    r = get_replacements(a)
    return xml_replace('model_regulament_intern.docx', [
        ('DANI ALIN', r['nume_complet']),
        ('26.05.2026', r['azi']),
    ])

def gen_cerere_concediu(a):
    r = get_replacements(a)
    return xml_replace('model_cerere_concediu.docx', [
        ('DANI ALIN', r['nume_complet']),
        ('contract de munca nr 243/26.05.2026', 'contract de munca nr ' + r['nr_contract'] + '/' + r['data_contract']),
        ('26.05.2026', r['data_contract']),
    ])

def gen_dispozitie_plata(a):
    r = get_replacements(a)
    
    # Folosim replace direct in XML (textul e fragmentat in run-uri)
    import zipfile, io as _io
    model_path = os.path.join(BASE_DIR, 'model_dispozitie_plata.docx')
    
    ci = v(a.get('ci_serie_nr', ''))
    ci_parts = ci.split(' ')
    ci_serie = ci_parts[0] if ci_parts else ''
    ci_nr = ''.join(ci_parts[1:]) if len(ci_parts) > 1 else ''
    functie_scurta = v(a.get('functie', '')).split(',')[0].upper()
    
    with open(model_path, 'rb') as f:
        model_bytes = f.read()
    
    zin = zipfile.ZipFile(_io.BytesIO(model_bytes))
    zout_buf = _io.BytesIO()
    
    with zipfile.ZipFile(zout_buf, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'word/document.xml':
                xml = data.decode('utf-8')
                xml = xml.replace('DANI ALIN', r['nume_complet'])
                xml = xml.replace('MUNCITOR NECALIFICAT', functie_scurta)
                xml = xml.replace('SX', ci_serie)
                xml = xml.replace('523319', ci_nr)
                data = xml.encode('utf-8')
            zout.writestr(item, data)
    
    zout_buf.seek(0)
    return zout_buf.read()

def gen_declaratie_lichidare(a):
    r = get_replacements(a)
    return xml_replace('model_declaratie_lichidare.docx', [
        ('DANI ALIN', r['nume_complet']),
        ('JIBOU', r['localitate']),
        ('str.STREJARILOR', 'str.' + r['strada']),
        ('nr. 94', 'nr. ___'),
        ('SALAJ', r['judet']),
        ('SX', r['ci_serie']),
        ('523319', r['ci_nr']),
        ('SPCLEP JIBOU', r['ci_elib']),
        ('06.01.2022', r['data_ci']),
        ('5020704313203', r['cnp']),
        ('nr. 243 din data de 26.05.2026', 'nr. ' + r['nr_contract'] + ' din data de ' + r['data_contract']),
        ('26.05.2026', r['data_contract']),
    ])

def gen_cerere_desfacere(a):
    r = get_replacements(a)
    return xml_replace('model_cerere_desfacere.docx', [
        ('DANI ALIN', r['nume_complet']),
        ('243/26.05.2026)', r['nr_contract'] + '/' + r['data_contract'] + ')'),
        ('26.05.2026', r['data_contract']),
    ])

def gen_cim(a):
    """Apelează generate_cim.py pentru CIM"""
    import subprocess
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, 'generate_cim.py'), json.dumps(a)],
        capture_output=True
    )
    if result.returncode != 0:
        raise Exception(result.stderr.decode())
    return result.stdout

def gen_all(a):
    """Generează toate documentele și le returnează ca ZIP"""
    r = get_replacements(a)
    name = f"{r['prenume']}_{r['nume']}"
    
    generators = [
        (f'1_CIM_{name}.docx', gen_cim),
        (f'2_Fisa_post_{name}.docx', gen_fisa_post),
        (f'3_Regulament_intern_{name}.docx', gen_regulament),
        (f'4_Cerere_concediu_{name}.docx', gen_cerere_concediu),
        (f'5_Dispozitie_plata_{name}.docx', gen_dispozitie_plata),
        (f'6_Declaratie_lichidare_{name}.docx', gen_declaratie_lichidare),
        (f'7_Cerere_desfacere_{name}.docx', gen_cerere_desfacere),
    ]
    
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, generator in generators:
            try:
                content = generator(a)
                zf.writestr(filename, content)
                print(f"  ✅ {filename}", file=sys.stderr)
            except Exception as e:
                print(f"  ❌ {filename}: {e}", file=sys.stderr)
    
    zip_buf.seek(0)
    return zip_buf.read()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python generate_docs.py <tip> '<json>'", file=sys.stderr)
        sys.exit(1)
    
    tip = sys.argv[1]
    a = json.loads(sys.argv[2])
    
    generators = {
        'cim': gen_cim,
        'fisa_post': gen_fisa_post,
        'regulament': gen_regulament,
        'cerere_concediu': gen_cerere_concediu,
        'dispozitie_plata': gen_dispozitie_plata,
        'declaratie_lichidare': gen_declaratie_lichidare,
        'cerere_desfacere': gen_cerere_desfacere,
        'all': gen_all,
    }
    
    if tip not in generators:
        print(f"Tip necunoscut: {tip}", file=sys.stderr)
        sys.exit(1)
    
    result = generators[tip](a)
    sys.stdout.buffer.write(result)

# ── ACTE ÎNCETARE CIM ─────────────────────────────────────────────────────────

def gen_incetare(a, extra):
    """Generează toate actele de încetare CIM ca ZIP."""
    import zipfile, io as _io
    
    tip_incetare = extra.get('tip_incetare', '55b')  # '55b' sau '31_3'
    nr_decizie = extra.get('nr_decizie', '___')
    data_incetare = fmt_date(extra.get('data_incetare')) if extra.get('data_incetare') else fmt_date(a.get('data_incetare', ''))
    zile_cfs = extra.get('zile_cfs', '00')
    zile_absente = extra.get('zile_absente', '00')
    nr_adeverinta = extra.get('nr_adeverinta', '___')
    
    r = get_replacements(a)
    azi = r['azi']
    
    # Date comune
    common = [
        ('BORASTEANU ION', r['nume_complet']),
        ('SZUCS VALENTIN-PATRIK', r['nume_complet']),
        ('1731114252327', r['cnp']),
        ('5020215303730', r['cnp']),
        ('183/23.03.2026', r['nr_contract'] + '/' + r['data_contract']),
        ('209/15.04.2026', r['nr_contract'] + '/' + r['data_contract']),
        ('23.03.2026', r['data_contract']),
        ('15.04.2026', r['data_contract']),
        ('23.04.2026', data_incetare),
        ('05.05.2026', data_incetare),
        ('24.03.2026', r['data_angajare']),
        ('16.04.2026', r['data_angajare']),
        ('DULGHER', r['functie'].split(',')[0].upper() if r['functie'] != '___________' else '___'),
        ('MUNCITOR NECALIFICAT', r['functie'].split(',')[0].upper() if r['functie'] != '___________' else '___'),
        ('COR-711501', ''),
        ('4582', r['salariu']),
    ]

    # Decizie încetare
    if tip_incetare == '55b':
        model_decizie = 'model_decizie_55b.docx'
        art_legal = 'art. 55 LIT B'
        art_adeverinta = 'art.55 lit.B'
    else:
        model_decizie = 'model_decizie_31_3.docx'
        art_legal = 'art. 31/3'
        art_adeverinta = 'art.31/alin.3.'

    decizie_replacements = common + [
        ('Nr. 330 din 04.05.2026', 'Nr. ' + nr_decizie + ' din ' + azi),
        ('Nr. 287 din 23.04.2026', 'Nr. ' + nr_decizie + ' din ' + azi),
        ('__00__', zile_cfs),
        ('__01__', zile_absente),
        ('__0__', zile_cfs),
    ]

    # Notificare perioadă probă
    notif_replacements = common + [
        ('Nr. de inregistrare  286/ 23.04.2026', 'Nr. de inregistrare  ' + nr_decizie + '/ ' + azi),
        ('286/ 23.04.2026', nr_decizie + '/ ' + azi),
    ]

    # Adeverință vechime
    adeverinta_replacements = common + [
        ('Nr. de inregistrare  288/ 23.04.2026', 'Nr. de inregistrare  ' + nr_adeverinta + '/ ' + azi),
        ('288/ 23.04.2026', nr_adeverinta + '/ ' + azi),
        ('TIMISOARA', r['localitate']),
        ('str. LABIRINT', 'str. ' + r['strada']),
        ('nr.4, Bl.-, Sc.-, Ap.18', 'nr. ___'),
        ('jud. TIMIS', 'jud. ' + r['judet']),
        ('TZ', r['ci_serie']),
        ('332193', r['ci_nr']),
        ('Nr. 287/23.04.2026', 'Nr. ' + nr_decizie + '/' + azi),
        ('287/23.04.2026', nr_decizie + '/' + azi),
        ('art.31/alin.3. - ', art_adeverinta + ' - '),
        ('art.55 lit.B - ', art_adeverinta + ' - '),
        ('01 zile calendaristice de absente nemotivate', zile_absente + ' zile calendaristice de absente nemotivate'),
        ('0 zile calendaristice de concediu fara plata', '0 zile calendaristice de concediu fara plata'),
        ('23.04.2026', data_incetare),
        ('DECIZIE INCETARE CIM\nNr. 287/23.04.2026', 'DECIZIE INCETARE CIM\nNr. ' + nr_decizie + '/' + azi),
        ('Incetat Contract de munca prin art.31/alin.3. Perioada de proba- L53/2003', 'Incetat Contract de munca prin ' + art_adeverinta + ' L53/2003'),
    ]

    zip_buf = _io.BytesIO()
    prefix = r['prenume'] + '_' + r['nume']
    
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f'1_Decizie_incetare_{prefix}.docx', xml_replace(model_decizie, decizie_replacements))
        if tip_incetare == '31_3':
            zf.writestr(f'2_Notificare_proba_{prefix}.docx', xml_replace('model_notificare_proba.docx', notif_replacements))
        zf.writestr(f'3_Adeverinta_vechime_{prefix}.docx', xml_replace('model_adeverinta_vechime.docx', adeverinta_replacements))
    
    zip_buf.seek(0)
    return zip_buf.read()
