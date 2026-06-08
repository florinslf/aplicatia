// generate-cim.js - Generator CIM prin find+replace în modelul original
// Copiați modelul CIM în același folder și redenumiți-l: model_cim.docx

const fs = require('fs');
const path = require('path');
const AdmZip = require('adm-zip');

// Încearcă să încarce AdmZip, altfel folosește metoda alternativă
let zipAvailable = false;
try { require.resolve('adm-zip'); zipAvailable = true; } catch(e) {}

async function generateCIM(a) {
  const modelPath = path.join(__dirname, 'model_cim.docx');
  
  if (!fs.existsSync(modelPath)) {
    throw new Error('Fișierul model_cim.docx nu există în folderul serverului. Copiați modelul și redenumiți-l model_cim.docx');
  }

  const fmt = d => {
    if (!d) return '___________';
    try { return new Date(d).toLocaleDateString('ro-RO', {day:'2-digit', month:'2-digit', year:'numeric'}); }
    catch(e) { return String(d); }
  };
  const v = x => x || '___________';
  const azi = fmt(new Date());
  const dataContract = a.data_contract || azi;
  const nrRevisal = a.nr_revisal || '___';
  const numePrenume = v(a.prenume) + ' ' + v(a.nume);

  // Citim zip-ul
  const modelBuffer = fs.readFileSync(modelPath);
  
  // Folosim unzip manual pentru a modifica XML-ul
  const AdmZipLib = require('adm-zip');
  const zip = new AdmZipLib(modelBuffer);
  
  // Citim document.xml
  let docXml = zip.readAsText('word/document.xml');
  
  // Funcție de replace care ține cont că textul poate fi împărțit în mai multe run-uri XML
  // Facem replace direct în textul XML, dar mai întâi "aplatizăm" run-urile adiacente
  
  // Replace simplu pentru valorile continue
  const replacements = [
    // Numele angajatului - apare de mai multe ori
    ['MICHI NELU-CLAUDIU', numePrenume.toUpperCase()],
    // Domiciliu  
    ['CLUJ NAPOCA', (v(a.domiciliu)).toUpperCase()],
    ['LIPSA DOMICILIU', ''],
    // CI
    ['PR ', (v(a.ci_serie_nr)).split(' ')[0] + ' '],
    ['358880', (v(a.ci_serie_nr)).split(' ')[1] || ''],
    ['SPCLEP CLUJ', v(a.ci_eliberat_de).toUpperCase()],
    ['10.11.2025', fmt(a.ci_data)],
    // CNP
    ['1960728125822', v(a.cnp)],
    // Data angajare
    ['07.05.2026', fmt(a.data_angajare)],
    // Data contract si revisal
    ['06.05.2026', dataContract],
    ['232', nrRevisal],
    // Functie
    ['MUNCITOR NECALIFICAT la demolarea cladirilor, captuseli, zidarie, placi mozaic, faianta, gresie, parchet cod COR 931301', v(a.functie)],
    ['MUNCITOR NECALIFICAT', v(a.functie).split(',')[0].toUpperCase()],
    // Salariu
    ['4582', a.salariu ? String(a.salariu) : '___________'],
  ];

  for (const [from, to] of replacements) {
    // Replace în text simplu (când e continuu în XML)
    docXml = docXml.split(from).join(to);
  }

  // Salvăm înapoi în zip
  zip.updateFile('word/document.xml', Buffer.from(docXml, 'utf8'));
  
  return zip.toBuffer();
}

module.exports = { generateCIM };
