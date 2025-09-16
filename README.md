# LexiCare 🧠💬 – Sistema AI per Referti Clinici

**LexiCare** è un motore di supporto decisionale per clinici, progettato per:
- 🩺 Analizzare semanticamente referti PDF (radiologia, laboratorio, patologia)
- ⚠️ Segnalare peggioramenti o miglioramenti nel tempo
- 💡 Ricevere feedback dai medici per migliorare nel tempo
- 📤 Esportare dataset per re-train del modello AI
- 🔄 Integrazione con sistemi EHR (Electronic Health Record)
- 🔐 Identificazione sicura tramite Codice Fiscale obbligatorio

---

## 🔧 Tecnologie
- **Backend**: FastAPI + PostgreSQL
- **AI**: MedGemma via Ollama
- **Frontend**: React (Vite) + TailwindCSS
- **PDF Parsing**: PyMuPDF (fitz) + OCR (Tesseract)

> **Nota**: Il binario di tailwindcss nella directory `frontend/tools/` è stato rimosso dal repository GitHub a causa delle limitazioni di dimensione dei file. Puoi installare tailwindcss tramite npm durante lo sviluppo.

---

## 🚀 Avvio (con Docker)

```bash
cp env.example .env
# Modifica le variabili in .env secondo necessità
docker-compose up --build
```

## 💻 Avvio manuale (sviluppo)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # su Windows: venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8006
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🧪 Test

```bash
pytest tests/
```

## 🔒 Requisiti per i Referti

### Codice Fiscale Obbligatorio per Salvataggio

Per garantire una corretta identificazione del paziente e tracciabilità dei referti, LexiCare richiede il **Codice Fiscale per il salvataggio permanente nel database**. I documenti senza Codice Fiscale:

- Verranno comunque analizzati dall'AI (diagnosi e classificazione)
- Verranno confrontati con referti precedenti dello stesso tipo nel database
- Non saranno salvati nel database permanentemente
- Saranno visualizzati con un avviso di "REFERTO ANALIZZATO (NON SALVATO)"

Il sistema cerca automaticamente il Codice Fiscale nel testo del referto utilizzando pattern matching avanzato. Questo approccio permette di ottenere analisi semantiche anche per referti anonimi o senza identificativo, pur mantenendo la tracciabilità nel database solo per pazienti correttamente identificati.

### Gestione dei Tipi di Referto

LexiCare estrae automaticamente il titolo esatto del referto dal documento (es. "Eccocardiografia", "TAC Torace", "Esami del Sangue") e lo salva nel campo `tipo_referto` del database. Questo titolo viene utilizzato per trovare referti esattamente dello stesso tipo per confronti precisi.

Il sistema supporta un numero illimitato di tipi di referto, senza alcuna categorizzazione o normalizzazione, permettendo un confronto molto preciso tra referti dello stesso tipo esatto. Per esempio:
- Due referti "TAC Torace" saranno confrontati tra loro
- Due referti "Eccocardiografia" saranno confrontati tra loro  
- Due referti "TAC Addome con Mezzo di Contrasto" saranno confrontati tra loro

Questo approccio permette di:
- Confrontare referti dello stesso tipo esatto (ad es. due "TAC Torace" dello stesso paziente)
- Mantenere la massima precisione evitando generalizzazioni o categorizzazioni
- Visualizzare l'evoluzione clinica del paziente per esami specifici
- Supportare qualsiasi tipo di referto senza limitazioni predefinite

---

## 🌐 Integrazione con sistemi EHR

LexiCare offre una API dedicata per l'integrazione con sistemi EHR (Electronic Health Record) esterni, permettendo:

- 📄 Invio di referti PDF per analisi
- 📊 Recupero di referti e risultati per uno specifico paziente
- 💬 Invio di feedback dei medici

### Autenticazione API

Tutte le richieste API EHR richiedono un header di autenticazione:

```
X-API-Key: your-api-key-here
```

Configura la tua API key nel file `.env`:

```
API_KEY=your-secure-api-key-here
```

### Configurazione CORS

Per consentire chiamate cross-origin dal tuo sistema EHR, aggiungi il dominio nel file `.env`:

```
EHR_DOMAIN_1=https://your-ehr-domain.com
EHR_DOMAIN_2=https://another-ehr-domain.com
```

### Endpoint API EHR

#### 1. Analizzare referti PDF

```http
POST /api/ehr/analyze
```

Parametri:
- `files`: Array di file PDF (max 5)

Risposta:
```json
{
  "risultati": [
    {
      "diagnosi_ai": "...",
      "classificazione_ai": "...",
      "codice_fiscale": "RSSMRA80A01H501U",
      "nome_paziente": "Mario Rossi",
      "tipo_referto": "TAC Torace",
      "data_referto": "15/05/2023",
      "salvato": true,
      "report_id": "uuid-here",
      "situazione": "stabile",
      "spiegazione": "Nessun cambiamento significativo"
    }
  ]
}
```

#### 2. Recuperare i referti di un paziente

```http
GET /api/ehr/patients/{codice_fiscale}/reports?report_type=radiologia
```

Parametri:
- `codice_fiscale`: Codice fiscale del paziente (path)
- `report_type`: Tipo di referto (query, opzionale)

Risposta:
```json
[
  {
    "id": "uuid-here",
    "patient_cf": "RSSMRA80A01H501U",
    "patient_name": "Mario Rossi",
    "report_type": "radiologia",
    "report_date": "2023-05-15T10:30:00",
    "ai_diagnosis": "Diagnosi AI",
    "ai_classification": "Normale",
    "doctor_diagnosis": null,
    "doctor_classification": null,
    "comparison_to_previous": "Stabile",
    "comparison_explanation": "Nessun cambiamento significativo"
  }
]
```

#### 3. Dettaglio di un singolo referto

```http
GET /api/ehr/patients/{codice_fiscale}/reports/{report_id}
```

Parametri:
- `codice_fiscale`: Codice fiscale del paziente (path)
- `report_id`: ID UUID del referto (path)

Risposta:
```json
{
  "id": "uuid-here",
  "patient_cf": "RSSMRA80A01H501U",
  "patient_name": "Mario Rossi",
  "report_type": "radiologia",
  "report_date": "2023-05-15T10:30:00",
  "ai_diagnosis": "Diagnosi AI",
  "ai_classification": "Normale",
  "doctor_diagnosis": null,
  "doctor_classification": null,
  "comparison_to_previous": "Stabile",
  "comparison_explanation": "Nessun cambiamento significativo",
  "extracted_text": "Testo completo del referto...",
  "doctor_comment": null,
  "created_at": "2023-05-15T10:30:00"
}
```

#### 4. Inviare feedback del medico

```http
POST /api/ehr/feedback
```

Body:
```json
{
  "report_id": "uuid-here",
  "diagnosi_corretta": "Diagnosi corretta dal medico",
  "classificazione_corretta": "Anomalia",
  "commento": "Nota aggiuntiva del medico"
}
```

Risposta:
```json
{
  "messaggio": "Feedback salvato correttamente."
}
```

#### 5. Ottenere tipi di referto supportati

```http
GET /api/ehr/report-types
```

Risposta:
```json
{
  "tipi_referto": ["radiologia", "laboratorio", "patologia"]
}
```

### Esempio di integrazione (JavaScript)

```javascript
async function analyzeReports(files) {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));
  
  const response = await fetch('https://your-lexicare-url.com/api/ehr/analyze', {
    method: 'POST',
    headers: {
      'X-API-Key': 'your-api-key-here'
    },
    body: formData
  });
  
  return await response.json();
}

async function getPatientReports(codiceFiscale, reportType = null) {
  let url = `https://your-lexicare-url.com/api/ehr/patients/${codiceFiscale}/reports`;
  if (reportType) {
    url += `?report_type=${reportType}`;
  }
  
  const response = await fetch(url, {
    headers: {
      'X-API-Key': 'your-api-key-here'
    }
  });
  
  return await response.json();
}
```

---

## 📝 Licenza
© 2023-2024 LexiCare - Tutti i diritti riservati
