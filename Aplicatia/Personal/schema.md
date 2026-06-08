# Schema Modul Personal

## Tabele

### `angajati`
Date complete despre fiecare angajat.

| Coloană | Tip | Obligatoriu |
|---|---|---|
| id | uuid | ✅ |
| prenume | text | ✅ |
| nume | text | ✅ |
| cnp | text | - |
| data_nastere | date | - |
| ci_serie_nr | text | - |
| ci_eliberat_de | text | - |
| ci_data | date | - |
| email | text | - |
| telefon | text | - |
| domiciliu | text | - |
| functie | text | - |
| departament | text | - |
| salariu | numeric | - |
| data_angajare | date | - |
| data_incetare | date | - |
| nr_contract | text | - |
| nr_revisal | text | - |
| status | text | - |
| created_at | timestamptz | - |
| updated_at | timestamptz | - |

### `documente`
Documente atașate angajaților (contracte, adeverințe, etc.)

| Coloană | Tip | Obligatoriu |
|---|---|---|
| id | uuid | ✅ |
| angajat_id | uuid (FK → angajati) | - |
| tip | text | ✅ |
| titlu | text | ✅ |
| data_doc | date | - |
| file_url | text | - |
| note | text | - |
| created_at | timestamptz | - |
| created_by | uuid | - |

### `santiere`
Șantierele firmei.

| Coloană | Tip | Obligatoriu |
|---|---|---|
| id | uuid | ✅ |
| nume | text | ✅ |
| locatie | text | - |
| status | text | - |
| created_at | timestamptz | - |

### `repartizari`
Alocarea angajaților pe șantiere.

| Coloană | Tip | Obligatoriu |
|---|---|---|
| id | uuid | ✅ |
| angajat_id | uuid (FK → angajati) | - |
| santier_id | uuid (FK → santiere) | - |
| data_start | date | ✅ |
| data_sfarsit | date | - |
| created_at | timestamptz | - |

### `pontaje`
Orele lucrate per angajat per șantier.

| Coloană | Tip | Obligatoriu |
|---|---|---|
| id | uuid | ✅ |
| angajat_id | uuid (FK → angajati) | - |
| santier_id | uuid (FK → santiere) | - |
| data | date | ✅ |
| ore | numeric | - |
| observatii | text | - |
| introdus_de | text | - |
| created_at | timestamptz | - |

## Relații
- `angajati` ← `documente` (un angajat poate avea mai multe documente)
- `angajati` ← `repartizari` → `santiere` (angajații sunt repartizați pe șantiere)
- `angajati` ← `pontaje` → `santiere` (orele sunt înregistrate per angajat per șantier)
