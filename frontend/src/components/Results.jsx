import React, { useState, useEffect } from "react";
import { submitFeedback } from "../api/lexicareApi";

function Results({ results }) {
  const [feedback, setFeedback] = useState({});
  const [submitting, setSubmitting] = useState({});
  const [hasWorsenedCondition, setHasWorsenedCondition] = useState(false);
  const [comparisonResults, setComparisonResults] = useState([]);
  // Remove expanded state - all cards will be expanded by default

  useEffect(() => {
    // Extract comparison results from all reports that have comparison data
    console.log("🔍 Processing results for comparison section:", results);
    
    // Debug: Log each result's save status and CF
    results?.forEach((r, i) => {
      console.log(`🔍 Result ${i}: salvato=${r.salvato}, CF=${r.codice_fiscale}, situazione=${r.situazione}`);
    });
    
    if (results && results.length > 0) {
      const comparisons = results
        .filter(r => {
          const hasComparison = r.situazione && r.spiegazione && 
                               r.situazione !== "nessun confronto disponibile" && 
                               r.situazione !== "errore";
          console.log(`📊 Report ${r.tipo_referto}: situazione='${r.situazione}', spiegazione='${r.spiegazione}', hasComparison=${hasComparison}`);
          return hasComparison;
        })
        .map((r, index) => ({
          situazione: r.situazione,
          spiegazione: r.spiegazione,
          paziente: r.nome_paziente || r.codice_fiscale || "Paziente",
          tipo_referto: r.tipo_referto || "Referto",
          titolo_referto: r.tipo_referto || "Referto",
          codice_fiscale: r.codice_fiscale,
          data_referto: r.data_referto,
          originalIndex: index
        }));
      
      console.log(`✅ Found ${comparisons.length} comparison results:`, comparisons);
      setComparisonResults(comparisons);
      
      // Check if any patient's condition has worsened
      const hasWorsened = comparisons.some(comp => comp.situazione && comp.situazione.toLowerCase() === "peggiorata");
      setHasWorsenedCondition(hasWorsened);
    }
  }, [results]);

  if (!results || !results.length) return null;

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
      case "lieve": return "bg-green-500";
      case "moderato": return "bg-yellow-500";
      case "grave": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getClassificationExplanation = (classificazione) => {
    if (!classificazione || classificazione === "non disponibile") return "";
    switch(classificazione.toLowerCase()) {
      case "lieve": return "Condizione di basso rischio che richiede monitoraggio di routine";
      case "moderato": return "Condizione che necessita di attenzione medica e controlli regolari";
      case "grave": return "Condizione critica che richiede intervento medico immediato";
      default: return "";
    }
  };

  const getSituationIcon = (situazione) => {
    if (!situazione) return null;
    switch(situazione.toLowerCase()) {
      case "migliorata":
        return (
          <span className="text-green-600 font-medium flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Migliorata
          </span>
        );
      case "peggiorata":
        return (
          <span className="text-red-600 font-medium flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
            </svg>
            Peggiorata
          </span>
        );
      case "invariata":
        return (
          <span className="text-gray-600 font-medium flex items-center">
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

  const getSituationExplanation = (situazione) => {
    if (!situazione) return "";
    switch(situazione.toLowerCase()) {
      case "migliorata":
        return "La condizione clinica mostra segni di miglioramento rispetto al referto precedente";
      case "peggiorata":
        return "La condizione clinica presenta un peggioramento che richiede attenzione medica";
      case "invariata":
        return "La condizione clinica rimane stabile senza cambiamenti significativi";
      default:
        return "";
    }
  };

  const getReportStatusDisplay = (report) => {
    if (report.salvato) {
      return {
        text: "✓ REFERTO SALVATO",
        color: "text-green-600",
        bgColor: "border-green-500"
      };
    } else if (report.status === 'duplicate') {
      return {
        text: "📄 REFERTO GIÀ PRESENTE NEL SISTEMA",
        color: "text-blue-600", 
        bgColor: "border-blue-500"
      };
    } else if (!report.codice_fiscale) {
      return {
        text: "⚠ REFERTO ANALIZZATO (NON SALVATO - CODICE FISCALE MANCANTE)",
        color: "text-yellow-600",
        bgColor: "border-yellow-500"
      };
    } else {
      return {
        text: "⚠ REFERTO NON SALVATO",
        color: "text-red-600",
        bgColor: "border-red-500"
      };
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
      
      {results.map((r, i) => {
        const statusInfo = getReportStatusDisplay(r);
        return (
        <div key={i} className="bg-white rounded-lg shadow-card overflow-hidden">
          {/* Header della scheda */}
          <div className={`p-4 border-l-4 ${statusInfo.bgColor}`}>
            <div>
              <p className={`font-semibold ${statusInfo.color} text-sm mb-1`}>
                {statusInfo.text}
              </p>
              <h3 className="font-bold text-lg text-gray-800">
                {r.tipo_referto || "Referto"}
              </h3>
            </div>
          </div>
          
          {/* Corpo della scheda - sempre espanso */}
          <div className="px-6 py-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Colonna sinistra */}
              <div>
                {/* Dati paziente */}
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-1">Dati paziente</p>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p><span className="font-medium">Codice Fiscale:</span> {r.codice_fiscale || "Non disponibile"}</p>
                    <p><span className="font-medium">Nome:</span> {r.nome_paziente || "Non disponibile"}</p>
                  </div>
                </div>

                {/* Dati esame */}
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-1">Dati esame</p>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p><span className="font-medium">Tipo di esame:</span> {r.tipo_referto || "Non specificato"}</p>
                    <p><span className="font-medium">Data esame:</span> {r.data_referto || "Non specificata"}</p>
                  </div>
                </div>

                {/* Risultato analisi AI */}
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-1">Risultato analisi AI</p>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p className="font-medium mb-1">Diagnosi:</p>
                    <p className="mb-3 px-3 py-2 bg-white rounded border border-gray-200">{r.diagnosi_ai || "Non disponibile"}</p>
                    
                    <p className="font-medium mb-1">Classificazione:</p> 
                    <div className="px-3 py-2 rounded border border-gray-200 bg-white">
                      <div className="flex items-center mb-2">
                        <span className={`inline-block px-3 py-1 rounded-full text-xs text-white font-medium ${getSeverityColor(r.classificazione_ai)} mr-2`}>
                          {r.classificazione_ai || "non disponibile"}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 italic">
                        {getClassificationExplanation(r.classificazione_ai)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Colonna destra - Feedback del medico */}
              {r.salvato && (
                <div className="border-l border-gray-200 pl-6">
                  <p className="text-sm text-gray-600 mb-3">Feedback del medico</p>
                  
                  <div className="space-y-4">
                    <div>
                      <label htmlFor={`diagnosi-${i}`} className="block text-sm font-medium text-gray-700 mb-1">
                        Diagnosi corretta
                      </label>
                      <input
                        id={`diagnosi-${i}`}
                        type="text"
                        value={feedback[i]?.diagnosi || ""}
                        onChange={(e) => handleInputChange(i, "diagnosi", e.target.value)}
                        placeholder="Inserisci diagnosi corretta"
                        className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label htmlFor={`class-${i}`} className="block text-sm font-medium text-gray-700 mb-1">
                        Classificazione corretta
                      </label>
                      <select
                        id={`class-${i}`}
                        value={feedback[i]?.classificazione || ""}
                        onChange={(e) => handleInputChange(i, "classificazione", e.target.value)}
                        className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">Seleziona gravità</option>
                        <option value="lieve">Lieve</option>
                        <option value="moderato">Moderato</option>
                        <option value="grave">Grave</option>
                      </select>
                    </div>
                    
                    <div>
                      <label htmlFor={`commento-${i}`} className="block text-sm font-medium text-gray-700 mb-1">
                        Note aggiuntive
                      </label>
                      <textarea
                        id={`commento-${i}`}
                        value={feedback[i]?.commento || ""}
                        onChange={(e) => handleInputChange(i, "commento", e.target.value)}
                        placeholder="Commenti opzionali"
                        rows="3"
                        className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    
                    <button
                      onClick={() => handleSubmitFeedback(i, r.report_id)}
                      disabled={submitting[i] || !feedback[i]?.diagnosi || !feedback[i]?.classificazione}
                      className={`w-full flex items-center justify-center py-2 px-4 rounded-md text-white font-medium ${
                        submitting[i] || !feedback[i]?.diagnosi || !feedback[i]?.classificazione
                          ? "bg-gray-300"
                          : "bg-blue-600 hover:bg-blue-700"
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
        );
      })}

      {/* Sezione di riepilogo comparazioni */}
      {comparisonResults.length > 0 && (
        <div className="mt-8 border-t pt-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Confronto con Referti Precedenti
          </h2>

          {/* Legend/Status Explanation */}
          <div className="mb-6 bg-gray-50 p-4 rounded-lg border">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">📊 Legenda stati di confronto:</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <div className="flex items-center p-2 bg-green-50 rounded border-l-2 border-green-500">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                <div>
                  <span className="font-medium text-green-800">MIGLIORATA</span>
                  <p className="text-green-700 text-xs mt-1">Condizione clinica in miglioramento</p>
                </div>
              </div>
              <div className="flex items-center p-2 bg-red-50 rounded border-l-2 border-red-500">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
                </svg>
                <div>
                  <span className="font-medium text-red-800">PEGGIORATA</span>
                  <p className="text-red-700 text-xs mt-1">Richiede attenzione medica</p>
                </div>
              </div>
              <div className="flex items-center p-2 bg-gray-100 rounded border-l-2 border-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 12H6" />
                </svg>
                <div>
                  <span className="font-medium text-gray-800">INVARIATA</span>
                  <p className="text-gray-700 text-xs mt-1">Condizione stabile</p>
                </div>
              </div>
            </div>
          </div>

          {/* Avviso di peggioramento */}
          {hasWorsenedCondition && (
            <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-bold text-red-800 mb-2">⚠️ Attenzione: Peggioramento rilevato</h3>
                  <div className="text-red-700">
                    <p className="mb-2">È stato rilevato un peggioramento della condizione in uno o più referti rispetto ai precedenti esami.</p>
                    <p className="font-medium">Si raccomanda vivamente:</p>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      <li>Controllo medico approfondito</li>
                      <li>Valutazione clinica immediata</li>
                      <li>Eventuale ripetizione degli esami</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Lista confronti */}
          <div className="space-y-4">
            {comparisonResults.map((comp, i) => (
              <div 
                key={i} 
                className={`p-4 rounded-lg border-l-4 ${
                  comp.situazione.toLowerCase() === "migliorata" ? "bg-green-50 border-green-500 border-l-green-500" : 
                  comp.situazione.toLowerCase() === "peggiorata" ? "bg-red-50 border-red-500 border-l-red-500" :
                  "bg-gray-50 border-gray-300 border-l-gray-300"
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <span className="font-semibold text-gray-800 mr-2">
                      {comp.paziente} - {comp.tipo_referto}
                    </span>
                    {comp.data_referto && (
                      <span className="text-sm text-gray-500">({comp.data_referto})</span>
                    )}
                  </div>
                  <div className="flex items-center">
                    {getSituationIcon(comp.situazione)}
                  </div>
                </div>
                
                {/* Status explanation */}
                <div className="mb-3 p-2 bg-blue-50 border-l-2 border-blue-200 rounded-md">
                  <p className="text-sm text-blue-800 font-medium">
                    ℹ️ {getSituationExplanation(comp.situazione)}
                  </p>
                </div>
                
                <div className={`p-3 rounded-md ${
                  comp.situazione.toLowerCase() === "migliorata" ? "bg-green-100" : 
                  comp.situazione.toLowerCase() === "peggiorata" ? "bg-red-100" :
                  "bg-gray-100"
                }`}>
                  <p className="text-gray-700 font-medium mb-1">Analisi del confronto:</p>
                  <p className="text-gray-800">{comp.spiegazione}</p>
                  
                  {comp.situazione.toLowerCase() === "peggiorata" && (
                    <div className="mt-3 p-2 bg-red-200 rounded-md">
                      <p className="text-red-800 text-sm font-medium">
                        ⚠️ Questo risultato indica un peggioramento che richiede attenzione medica immediata.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Results;
