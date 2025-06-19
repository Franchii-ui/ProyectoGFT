const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

export async function transcribeVideo(file: File, language?: string) {
  const formData = new FormData();
  formData.append('file', file);
  if (language) {
    formData.append('language', language);
  }

  const response = await fetch(`${API_URL}/transcribe/`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to transcribe video');
  }

  return response.json();
}

export async function getTranscription(fileId: string) {
  const response = await fetch(`${API_URL}/download/${fileId}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch transcription');
  }
  
  return response.text();
}

export async function exportTranscription(fileId: string, format: 'docx' | 'pdf' | 'html' | 'txt') {
  window.open(`${API_URL}/export/${fileId}?format=${format}`, '_blank');
}

export async function saveTranscription(fileId: string, text: string) {
  const response = await fetch(`${API_URL}/save/${fileId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to save transcription');
  }

  return response.json();
}