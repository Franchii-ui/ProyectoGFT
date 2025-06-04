// src/components/react/ResultViewer.jsx
const ResultViewer = ({ result, onDownload }) => {
  if (!result) return null;

  return (
    <div className="mt-6 p-4 border border-green-200 bg-green-50 rounded-lg">
      <h3 className="font-bold text-green-800 mb-2">¡Procesamiento completado!</h3>
      
      {result.summary && (
        <div className="mb-3">
          <h4 className="font-semibold text-green-700">Resumen:</h4>
          <p className="text-green-600">{result.summary}</p>
        </div>
      )}

      {result.keyPoints && (
        <div className="mb-4">
          <h4 className="font-semibold text-green-700">Puntos clave:</h4>
          <ul className="list-disc pl-5 text-green-600">
            {result.keyPoints.map((point, index) => (
              <li key={index}>{point}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        onClick={onDownload}
        className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded"
      >
        Descargar Documento
      </button>
    </div>
  );
};

export default ResultViewer;