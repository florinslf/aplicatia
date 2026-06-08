const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');
const { execFile, spawn } = require('child_process');

const PORT = process.env.PORT || 3000;
const MIME = {
  '.html': 'text/html', '.js': 'application/javascript',
  '.css': 'text/css', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.pdf': 'application/pdf',
};

// Detectăm Python disponibil
function findPython(cb) {
  const cmds = ['python3', 'python'];
  let i = 0;
  function tryNext() {
    if (i >= cmds.length) { cb(null); return; }
    execFile(cmds[i], ['--version'], (err) => {
      if (!err) cb(cmds[i]);
      else { i++; tryNext(); }
    });
  }
  tryNext();
}

let pythonCmd = null;
findPython(cmd => {
  pythonCmd = cmd;
  if (cmd) console.log(`  ✅ Python găsit: ${cmd}`);
  else console.log('  ⚠️  Python negăsit. Instalați Python pentru generare DOCX.');
});

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-api-key, anthropic-version');

  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  // ── API: Generare CIM DOCX ────────────────────────────────────────────────
  if (pathname === '/api/generate-cim' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const angajat = JSON.parse(body);
        
        if (!pythonCmd) {
          res.writeHead(503, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Python nu este instalat pe server.' }));
          return;
        }

        const scriptPath = path.join(__dirname, 'generate_cim.py');
        if (!fs.existsSync(scriptPath)) {
          res.writeHead(503, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'generate_cim.py lipsește din folder.' }));
          return;
        }

        const modelPath = path.join(__dirname, 'model_cim.docx');
        if (!fs.existsSync(modelPath)) {
          res.writeHead(503, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'model_cim.docx lipsește din folder.' }));
          return;
        }

        const chunks = [];
        const errChunks = [];
        const proc = spawn(pythonCmd, [scriptPath, JSON.stringify(angajat)]);
        
        proc.stdout.on('data', d => chunks.push(d));
        proc.stderr.on('data', d => errChunks.push(d));
        
        proc.on('close', code => {
          if (code !== 0) {
            const errMsg = Buffer.concat(errChunks).toString();
            console.error('Python error:', errMsg);
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: errMsg }));
            return;
          }
          
          const docxBuffer = Buffer.concat(chunks);
          const prenume = angajat.prenume || '';
          const nume = angajat.nume || '';
          const filename = `CIM_${prenume}_${nume}.docx`.replace(/\s+/g, '_');
          
          res.writeHead(200, {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'Content-Disposition': `attachment; filename="${filename}"`,
            'Content-Length': docxBuffer.length,
            'Access-Control-Allow-Origin': '*'
          });
          res.end(docxBuffer);
          console.log(`  📄 CIM generat pentru ${prenume} ${nume} (${docxBuffer.length} bytes)`);
        });

        proc.on('error', err => {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: err.message }));
        });

      } catch(e) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // ── API: Generare acte încetare CIM ─────────────────────────────────────
  if (pathname === '/api/generate-incetare' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const parsed = JSON.parse(body);
        const angajat = parsed.angajat;
        const extra = parsed.extra;
        const scriptPath = path.join(__dirname, 'generate_incetare.py');
        const chunks = [];
        const errChunks = [];
        const proc = spawn(pythonCmd, [scriptPath, JSON.stringify({ angajat, extra })]);
        proc.stdout.on('data', d => chunks.push(d));
        proc.stderr.on('data', d => { errChunks.push(d); process.stdout.write(d); });
        proc.on('close', code => {
          if (code !== 0) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: Buffer.concat(errChunks).toString() }));
            return;
          }
          const buf = Buffer.concat(chunks);
          const sanitize = s => (s || '').replace(/[^a-zA-Z0-9_-]/g, '_');
          const filename = 'Acte_incetare_' + sanitize(angajat.prenume) + '_' + sanitize(angajat.nume) + '.zip';
          res.writeHead(200, {
            'Content-Type': 'application/zip',
            'Content-Disposition': 'attachment; filename="' + filename + '"',
            'Content-Length': buf.length,
            'Access-Control-Allow-Origin': '*'
          });
          res.end(buf);
          console.log('  Acte incetare generate pentru ' + angajat.prenume + ' ' + angajat.nume);
        });
        proc.on('error', err => {
          res.writeHead(500);
          res.end(JSON.stringify({ error: err.message }));
        });
      } catch(e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // ── API: Generare toate documentele (ZIP) ───────────────────────────────
  if (pathname === '/api/generate-docs' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const tip = data.tip || 'all';
        const angajat = data.angajat;
        
        if (!pythonCmd) {
          res.writeHead(503, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Python indisponibil.' }));
          return;
        }

        const scriptPath = path.join(__dirname, 'generate_docs.py');
        const chunks = [];
        const errChunks = [];
        const proc = spawn(pythonCmd, [scriptPath, tip, JSON.stringify(angajat)]);
        
        proc.stdout.on('data', d => chunks.push(d));
        proc.stderr.on('data', d => { errChunks.push(d); process.stdout.write(d); });
        
        proc.on('close', code => {
          if (code !== 0) {
            const errMsg = Buffer.concat(errChunks).toString();
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: errMsg }));
            return;
          }
          const buf = Buffer.concat(chunks);
          const prenume = angajat.prenume || '';
          const nume = angajat.nume || '';
          const isZip = tip === 'all';
          // Sanitize filename - remove diacritics and special chars
          const sanitize = s => (s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-zA-Z0-9_-]/g,'_');
          const filename = isZip 
            ? `Dosar_${sanitize(prenume)}_${sanitize(nume)}.zip`
            : `${tip}_${sanitize(prenume)}_${sanitize(nume)}.docx`;
          const contentType = isZip
            ? 'application/zip'
            : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
          
          res.writeHead(200, {
            'Content-Type': contentType,
            'Content-Disposition': `attachment; filename="${filename.replace(/\s+/g,'_')}"`,
            'Content-Length': buf.length,
            'Access-Control-Allow-Origin': '*'
          });
          res.end(buf);
          console.log(`  📦 Dosar generat pentru ${prenume} ${nume} (${buf.length} bytes)`);
        });
        
        proc.on('error', err => {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: err.message }));
        });
      } catch(e) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // ── API: Proxy Claude ─────────────────────────────────────────────────────
  if (pathname === '/api/claude' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      const options = {
        hostname: 'api.anthropic.com', port: 443, path: '/v1/messages', method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': process.env.ANTHROPIC_API_KEY || req.headers['x-api-key'] || '',
          'anthropic-version': '2023-06-01',
          'Content-Length': Buffer.byteLength(body)
        }
      };
      const proxyReq = https.request(options, proxyRes => {
        res.writeHead(proxyRes.statusCode, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
        proxyRes.pipe(res);
      });
      proxyReq.on('error', err => { res.writeHead(500); res.end(JSON.stringify({ error: err.message })); });
      proxyReq.write(body);
      proxyReq.end();
    });
    return;
  }

  // ── API: Config Supabase ─────────────────────────────────────────────────
  if (pathname === '/api/config' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
    res.end(JSON.stringify({
      supabaseUrl: process.env.SUPABASE_URL || '',
      supabaseKey: process.env.SUPABASE_ANON_KEY || ''
    }));
    return;
  }

  // ── Fișiere statice ───────────────────────────────────────────────────────
  let filePath = '.' + pathname;
  if (pathname === '/') filePath = './hr-contracte.html';
  const ext = path.extname(filePath);
  const contentType = MIME[ext] || 'application/octet-stream';
  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(err.code === 'ENOENT' ? 404 : 500); res.end(err.code === 'ENOENT' ? '404 Not Found' : 'Server Error'); return; }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
});

server.listen(PORT, () => {
  console.log('');
  console.log('  ✅ Server HR Contracte pornit!');
  console.log('');
  console.log('  Deschideți în browser:');
  console.log('  👉  http://localhost:' + PORT);
  console.log('');
  console.log('  Pentru a opri serverul: Ctrl+C');
  console.log('');
});
