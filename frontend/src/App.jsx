import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import Results from "./components/Results";

function App() {
  const [results, setResults] = useState([]);

  return (
    <div className="min-h-screen bg-neutral-light flex flex-col">
      {/* Header */}
      <header className="bg-sanitario text-white shadow-md">
        <div className="max-w-6xl mx-auto py-4 px-6 flex items-center justify-between">
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
            <h1 className="text-2xl font-bold tracking-tight">LexiCare</h1>
          </div>
          <p className="text-sm md:text-base font-medium">Sistema AI per Referti Clinici</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        <div className="max-w-6xl mx-auto py-8 px-6">
          <UploadForm setResults={setResults} />
          <Results results={results} />
          
          {!results.length && (
            <div className="text-center mt-16">
              <div className="bg-white rounded-lg shadow-card p-8 max-w-lg mx-auto">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4 text-neutral-light" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h2 className="text-xl font-medium text-neutral-dark mb-2">Nessun referto analizzato</h2>
                <p className="text-neutral">
                  Carica i tuoi referti in formato PDF per ottenere un'analisi semantica automatica e confrontare l'evoluzione nel tempo.
                </p>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white py-4 px-6 border-t border-gray-200">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center text-sm text-neutral">
          <div className="mb-3 md:mb-0">
            <p>© {new Date().getFullYear()} LexiCare - Sistema AI per supporto decisionale clinico</p>
          </div>
          <div className="flex space-x-6">
            <a href="#" className="hover:text-sanitario">Documentazione</a>
            <a href="#" className="hover:text-sanitario">Supporto</a>
            <a href="#" className="hover:text-sanitario">Privacy</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
