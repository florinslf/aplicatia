# Modul Personal — HR Contracte
**Firma:** Silbet Invest  
**Deployed:** Railway  
**Repo:** https://github.com/florinslf/hr-contracte

---

## Stack tehnic

| Componentă | Tehnologie |
|---|---|
| Frontend | HTML single-file (`hr-contracte.html`) |
| Backend / Server | Node.js (`server.js`) |
| Bază de date + Auth | Supabase (PostgreSQL) |
| Generare documente | Python (`generate_*.py`) + template-uri `.docx` |
| AI integrat | Claude API (proxy prin server) |

---

## Ce face aplicația

- **Gestiune angajați** — adăugare, editare, vizualizare fișă completă
- **Generare documente Word** — CIM, acte încetare, adeverințe, fișă post etc.
- **Pontaje** — ore lucrate per angajat per șantier
- **Repartizări** — alocarea angajaților pe șantiere
- **Autentificare** — login cu email/parolă prin Supabase Auth

---

## API endpoints (server.js)

| Endpoint | Metodă | Descriere |
|---|---|---|
| `/api/generate-cim` | POST | Generează CIM în format .docx |
| `/api/generate-incetare` | POST | Generează acte încetare CIM (.zip) |
| `/api/generate-docs` | POST | Generează dosar complet (.zip) sau un document specific |
| `/api/claude` | POST | Proxy către Claude API (AI chat) |
| `/api/config` | GET | Returnează credențialele Supabase |

---

## Template-uri documente disponibile

- `model_cim.docx` — Contract Individual de Muncă
- `model_adeverinta_vechime.docx`
- `model_cerere_concediu.docx`
- `model_cerere_desfacere.docx`
- `model_decizie_31_3.docx`
- `model_decizie_55b.docx`
- `model_declaratie_lichidare.docx`
- `model_dispozitie_plata.docx`
- `model_fisa_post.docx`
- `model_notificare_proba.docx`
- `model_regulament_intern.docx`

---

## Structură bază de date

Vezi `schema.md` pentru detalii complete.

**Tabele:** `angajati`, `documente`, `santiere`, `repartizari`, `pontaje`
