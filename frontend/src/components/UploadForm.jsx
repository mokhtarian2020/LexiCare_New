// src/components/UploadForm.jsx

import React, { useState } from "react";
import { analyzeDocuments } from "../api/lexicareApi";

const UploadForm = ({ setResults }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0 || files.length > 5) {
      alert("Seleziona da 1 a 5 file PDF.");
      return;
    }

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    setLoading(true);
    try {
      const data = await analyzeDocuments(formData);
      setResults(data.risultati);
    } catch (err) {
      console.error(err);
      alert("Errore durante l'analisi dei referti.");
    } finally {
      setLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const selectedFiles = Array.from(e.dataTransfer.files).filter(
        file => file.type === "application/pdf"
      );
      if (selectedFiles.length > 0) {
        setFiles(selectedFiles);
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-card p-6 mb-6 border-l-4 border-sanitario">
      <h2 className="text-xl font-semibold mb-4 text-neutral-dark flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-sanitario" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Carica Referti Medici (PDF)
      </h2>
      
      <div 
        className={`border-2 border-dashed rounded-lg p-8 mb-4 text-center transition-all ${
          dragActive ? "border-primary bg-primary-light" : "border-gray-300 hover:border-primary"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto mb-3 text-sanitario" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        
        <p className="text-gray-600 mb-2">Trascina qui i file PDF oppure</p>
        
        <input
          id="file-upload"
          type="file"
          accept=".pdf"
          multiple
          onChange={(e) => setFiles(Array.from(e.target.files))}
          className="hidden"
        />
        
        <label 
          htmlFor="file-upload" 
          className="inline-block bg-primary-light text-primary hover:bg-primary hover:text-white font-medium px-4 py-2 rounded-md cursor-pointer transition-colors"
        >
          Seleziona file
        </label>
        
        {files.length > 0 && (
          <div className="mt-4 text-left">
            <p className="font-medium text-neutral-dark">File selezionati ({files.length}):</p>
            <ul className="list-disc list-inside text-sm text-gray-600 mt-1">
              {Array.from(files).map((file, i) => (
                <li key={i}>{file.name}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      <div className="flex items-center">
        <button
          type="submit"
          className="bg-sanitario hover:bg-primary-dark text-white font-medium px-6 py-3 rounded-lg transition-colors flex items-center"
          disabled={loading}
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analisi in corso...
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Analizza Referti
            </>
          )}
        </button>
        
        <p className="text-sm text-neutral ml-4">
          Solo referti con Codice Fiscale valido verranno salvati nel sistema.
        </p>
      </div>
    </form>
  );
};

export default UploadForm;
