# Modificare: Arhivă Șantiere

## PASUL 1 — Supabase SQL Editor

```sql
ALTER TABLE santiere ADD COLUMN arhivat boolean DEFAULT false;
ALTER TABLE santiere ADD COLUMN arhivat_at timestamptz;
```

---

## PASUL 2 — hr-contracte.html

### Bloc 1: înlocuiește funcția `renderSantiere()` (liniile ~2561–2594)

```javascript
async function renderSantiere() {
  setTopbar('Șantiere', '<button class="btn btn-primary btn-sm" onclick="openModalSantier()">+ Șantier nou</button>');
  document.getElementById('content').innerHTML = '<div class="loading"><span class="spinner"></span>Se încarcă...</div>';

  const { data: active } = await supabase.from('santiere').select('*').neq('arhivat', true).order('created_at', { ascending: false });
  const { data: arhivate } = await supabase.from('santiere').select('*').eq('arhivat', true).order('arhivat_at', { ascending: false });
  const list = active || [];
  const arch = arhivate || [];

  document.getElementById('content').innerHTML = `
    <div class="card">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Șantier</th><th>Locație</th><th>Status</th><th>Angajați repartizați</th><th>Acțiuni</th></tr></thead>
          <tbody>
            ${list.length === 0 ? `<tr><td colspan="5"><div class="empty" style="padding:2rem;">
              <h3>Niciun șantier activ</h3><p>Adăugați primul șantier.</p>
            </div></td></tr>` : ''}
            ${list.map(s => `
              <tr>
                <td><div class="cell-name">${s.nume}</div></td>
                <td style="font-size:12px;color:var(--text2);">${s.locatie || '—'}</td>
                <td><span class="badge badge-${s.status === 'activ' ? 'green' : s.status === 'finalizat' ? 'blue' : 'amber'}">${s.status}</span></td>
                <td><button class="btn btn-secondary btn-sm" onclick="openRepartizari('${s.id}','${s.nume}')">👷 Repartizare</button></td>
                <td>
                  <div style="display:flex;gap:4px;">
                    <button class="btn btn-secondary btn-sm" onclick="openModalSantier('${s.id}','${s.nume}','${s.locatie||''}','${s.status}')">✏️</button>
                    <button class="btn btn-danger btn-sm" onclick="arhiveazaSantier('${s.id}','${s.nume}')">🗂️ Arhivează</button>
                  </div>
                </td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
    </div>

    ${arch.length > 0 ? `
    <div class="card" style="margin-top:1.5rem;">
      <div class="folder-title" style="padding:1rem 1.5rem;font-weight:600;border-bottom:1px solid var(--border);">🗂️ Arhivă Șantiere (${arch.length})</div>
      <div class="danger-zone" style="margin:1rem 1.5rem;">ℹ️ Șantierele arhivate nu mai apar în liste. Apasă <strong>Șterge definitiv</strong> pentru eliminare permanentă.</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Șantier</th><th>Locație</th><th>Arhivat la</th><th>Acțiuni</th></tr></thead>
          <tbody>
            ${arch.map(s => `
              <tr>
                <td><div class="cell-name" style="opacity:0.7;">${s.nume}</div></td>
                <td style="font-size:12px;color:var(--text2);">${s.locatie || '—'}</td>
                <td style="font-size:12px;color:var(--text2);">${s.arhivat_at ? new Date(s.arhivat_at).toLocaleDateString('ro-RO') : '—'}</td>
                <td>
                  <div style="display:flex;gap:4px;">
                    <button class="btn btn-secondary btn-sm" onclick="restaureazaSantier('${s.id}','${s.nume}')">↩️ Restaurează</button>
                    <button class="btn btn-danger btn-sm" onclick="stergeSantierDefinitiv('${s.id}','${s.nume}')">💀 Șterge definitiv</button>
                  </div>
                </td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
    </div>` : ''}`;
}
```

---

### Bloc 2: înlocuiește funcția `stergeSantier()` (liniile ~2623–2627)

```javascript
async function arhiveazaSantier(id, nume) {
  if (!confirm('Arhivezi șantierul "' + nume + '"?\nVa dispărea din lista activă dar poate fi restaurat sau șters definitiv din Arhivă.')) return;
  await supabase.from('santiere').update({ arhivat: true, arhivat_at: new Date().toISOString() }).eq('id', id);
  renderSantiere();
}

async function restaureazaSantier(id, nume) {
  if (!confirm('Restaurezi șantierul "' + nume + '" înapoi în lista activă?')) return;
  await supabase.from('santiere').update({ arhivat: false, arhivat_at: null }).eq('id', id);
  renderSantiere();
}

async function stergeSantierDefinitiv(id, nume) {
  if (!confirm('⚠️ Ștergi DEFINITIV șantierul "' + nume + '"?\nAceastă acțiune nu poate fi anulată.')) return;
  await supabase.from('santiere').delete().eq('id', id);
  renderSantiere();
}
```
