import React, { useState } from "react";
import { submitFeedback } from "../api/lexicareApi";

function Results({ results }) {
  const [feedback, setFeedback] = useState({});
  const [submitting, setSubmitting] = useState({});
  const [expanded, setExpanded] = useState({});

  if (!results.length) return null;

  const toggleExpand = (index) => {
    setExpanded({ ...expanded, [index]: !expanded[index] });
  };

  const handleInputChange = (index, field, value) => {
    setFeedback({
      ...feedback,
      [index]: { ...(feedback[index] || {}), [field]: value }
    });
  };

  const handleSubmitFeedback = async (index, reportId) => {
    if (!reportId || !feedback[index]) return;
    
    setSubmitting({ ...submitting, [index]: true });
    try {
      await submitFeedback({
        report_id: reportId,
        diagnosi_corretta: feedback[index].diagnosi || "",
        classificazione_corretta: feedback[index].classificazione || "",
        commento: feedback[index].commento || ""
      });
      
      // Feedback inviato con successo
      alert("Feedback inviato correttamente. Grazie per il contributo!");
      
      // Reset del form
      setFeedback({ ...feedback, [index]: null });
    } catch (error) {
      console.error("Errore nell'invio feedback:", error);
      alert("Errore nell'invio del feedback. Riprova più tardi.");
    } finally {
      setSubmitting({ ...submitting, [index]: false });
    }
  };

  const getSeverityColor = (classificazione) => {
    if (!classificazione || classificazione === "non disponibile") return "bg-gray-500";
    switch(classificazione.toLowerCase()) {
      case "lieve": return "bg-secondary";
      case "moderato": return "bg-warning";
      case "grave": return "bg-danger";
      default: return "bg-gray-500";
    }
  };

  const getSituationIcon = (situazione) => {
    if (!situazione) return null;
    switch(situazione.toLowerCase()) {
      case "migliorata":
        return (
          <span className="text-secondary-dark font-medium flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Migliorata
          </span>
        );
      case "peggiorata":
        return (
          <span className="text-danger-dark font-medium flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
            </svg>
            Peggiorata
          </span>
        );
      case "invariata":
        return (
          <span className="text-neutral-dark font-medium flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 12H6" />
            </svg>
            Invariata
          </span>
        );
      default:
        return situazione;
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-neutral-dark mb-4 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-sanitario" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Risultati Analisi ({results.length})
      </h2>
      
      {results.map((r, i) => (
        <div key={i} className={`bg-white rounded-lg shadow-card overflow-hidden transition-all ${expanded[i] ? "shadow-card-hover" : ""}`}>
          {/* Header della scheda */}
          <div className={`p-4 border-l-4 ${r.salvato ? "border-secondary" : "border-warning"} flex justify-between`}>
            <div>
              <p className={`font-semibold ${r.salvato ? "text-secondary" : "text-warning-dark"} text-sm mb-1`}>
                {r.salvato ? "✓ REFERTO SALVATO" : "⚠ NON SALVATO (CODICE FISCALE MANCANTE)"}
              </p>
              <h3 className="font-bold text-lg text-neutral-dark">
                {r.tipo_referto || "Referto"}
                {r.data_referto && <span className="text-sm font-normal text-neutral ml-2">del {r.data_referto}</span>}
              </h3>
            </div>
            <button 
              onClick={() => toggleExpand(i)}
              className="text-neutral hover:text-neutral-dark"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className={`h-6 w-6 transform transition-transform ${expanded[i] ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
          
          {/* Corpo della scheda */}
          <div className={`px-6 overflow-hidden transition-all ${expanded[i] ? "max-h-[1000px] py-6" : "max-h-0"}`}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Colonna sinistra */}
              <div>
                <div className="mb-4">
                  <p className="text-sm text-neutral mb-1">Dati paziente</p>
                  <div className="bg-neutral-light p-3 rounded-md">
                    <p><span className="font-medium">Codice Fiscale:</span> {r.codice_fiscale || "—"}</p>
                    <p><span className="font-medium">Nome:</span> {r.nome_paziente || "—"}</p>
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-sm text-neutral mb-1">Risultato analisi AI</p>
                  <div className="bg-neutral-light p-3 rounded-md">
                    <p><span className="font-medium">Diagnosi:</span> {r.diagnosi_ai}</p>
                    <p>
                      <span className="font-medium">Classificazione:</span> 
                      <span className={`ml-2 inline-block px-2 py-1 rounded-full text-xs text-white ${getSeverityColor(r.classificazione_ai)}`}>
                        {r.classificazione_ai || "non disponibile"}
                      </span>
                    </p>
                  </div>
                </div>
                
                {r.situazione && (
                  <div>
                    <p className="text-sm text-neutral mb-1">Confronto con precedenti</p>
                    <div className="bg-neutral-light p-3 rounded-md">
                      <p className="mb-2">
                        <span className="font-medium">Situazione:</span> 
                        <span className="ml-2">{getSituationIcon(r.situazione)}</span>
                      </p>
                      <p><span className="font-medium">Spiegazione:</span> {r.spiegazione}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Colonna destra - Feedback del medico */}
              {r.salvato && (
                <div className="border-l border-gray-200 pl-6">
                  <p className="text-sm text-neutral mb-3">Feedback del medico</p>
                  
                  <div className="space-y-4">
                    <div>
                      <label htmlFor={`diagnosi-${i}`} className="block text-sm font-medium text-neutral-dark mb-1">
                        Diagnosi corretta
                      </label>
                      <input
                        id={`diagnosi-${i}`}
                        type="text"
                        value={feedback[i]?.diagnosi || ""}
                        onChange={(e) => handleInputChange(i, "diagnosi", e.target.value)}
                        placeholder="Inserisci diagnosi corretta"
                        className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label htmlFor={`class-${i}`} className="block text-sm font-medium text-neutral-dark mb-1">
                        Classificazione corretta
                      </label>
                      <select
                        id={`class-${i}`}
                        value={feedback[i]?.classificazione || ""}
                        onChange={(e) => handleInputChange(i, "classificazione", e.target.value)}
                        className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="">Seleziona gravità</option>
                        <option value="lieve">Lieve</option>
                        <option value="moderato">Moderato</option>
                        <option value="grave">Grave</option>
                      </select>
                    </div>
                    
                    <div>
                      <label htmlFor={`commento-${i}`} className="block text-sm font-medium text-neutral-dark mb-1">
                        Note aggiuntive
                      </label>
                      <textarea
                        id={`commento-${i}`}
                        value={feedback[i]?.commento || ""}
                        onChange={(e) => handleInputChange(i, "commento", e.target.value)}
                        placeholder="Commenti opzionali"
                        rows="3"
                        className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    
                    <button
                      onClick={() => handleSubmitFeedback(i, r.report_id)}
                      disabled={submitting[i] || !feedback[i]?.diagnosi || !feedback[i]?.classificazione}
                      className={`w-full flex items-center justify-center py-2 px-4 rounded-md text-white font-medium ${
                        submitting[i] || !feedback[i]?.diagnosi || !feedback[i]?.classificazione
                          ? "bg-gray-300"
                          : "bg-primary hover:bg-primary-dark"
                      }`}
                    >
                      {submitting[i] ? (
                        <>
                          <svg className="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Invio in corso...
                        </>
                      ) : "Invia feedback"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default Results;
