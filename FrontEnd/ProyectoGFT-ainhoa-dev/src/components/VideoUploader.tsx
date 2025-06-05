import { useState } from 'react';
import { transcribeVideo } from '../services/api';

export default function VideoUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);
  const [transcription, setTranscription] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await transcribeVideo(file, language || undefined);
      
      if (result.success) {
        setFileId(result.file_id);
        setTranscription(result.transcription || '');
      } else {
        setError(result.message || 'Failed to transcribe video');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Video Transcription</h1>
      
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="mb-4">
          <label htmlFor="file" className="block mb-2">
            Select Video or Audio File:
          </label>
          <input
            type="file"
            id="file"
            accept=".mp4,.mp3,.wav,.m4a,.mov,.avi"
            onChange={handleFileChange}
            className="w-full p-2 border rounded"
          />
        </div>
        
        <div className="mb-4">
          <label htmlFor="language" className="block mb-2">
            Language (optional):
          </label>
          <input
            type="text"
            id="language"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            placeholder="e.g., en, es, fr"
            className="w-full p-2 border rounded"
          />
        </div>
        
        <button
          type="submit"
          disabled={loading || !file}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-blue-300"
        >
          {loading ? 'Transcribing...' : 'Transcribe'}
        </button>
      </form>
      
      {error && (
        <div className="p-4 mb-4 bg-red-100 text-red-700 rounded">
          Error: {error}
        </div>
      )}
      
      {transcription && (
        <div className="mt-6">
          <h2 className="text-xl font-bold mb-2">Transcription Results</h2>
          <div className="p-4 bg-gray-100 rounded whitespace-pre-wrap">
            {transcription}
          </div>
          
          {fileId && (
            <div className="mt-4">
              <p>Download as:</p>
              <div className="flex gap-2 mt-2">
                <button 
                  onClick={() => window.open(`http://localhost:8000/export/${fileId}?format=txt`, '_blank')}
                  className="px-3 py-1 bg-gray-600 text-white rounded"
                >
                  TXT
                </button>
                <button 
                  onClick={() => window.open(`http://localhost:8000/export/${fileId}?format=docx`, '_blank')}
                  className="px-3 py-1 bg-gray-600 text-white rounded"
                >
                  DOCX
                </button>
                <button 
                  onClick={() => window.open(`http://localhost:8000/export/${fileId}?format=pdf`, '_blank')}
                  className="px-3 py-1 bg-gray-600 text-white rounded"
                >
                  PDF
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}