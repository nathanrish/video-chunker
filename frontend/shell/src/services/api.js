const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5004';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async getHealth() {
    return this.request('/health');
  }

  // Meetings
  async getMeetings(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/api/meetings?${queryString}` : '/api/meetings';
    return this.request(endpoint);
  }

  async getMeeting(id) {
    return this.request(`/api/meetings/${id}`);
  }

  async createMeeting(meetingData) {
    return this.request('/api/meetings', {
      method: 'POST',
      body: JSON.stringify(meetingData),
    });
  }

  async updateMeeting(id, meetingData) {
    return this.request(`/api/meetings/${id}`, {
      method: 'PUT',
      body: JSON.stringify(meetingData),
    });
  }

  async deleteMeeting(id) {
    return this.request(`/api/meetings/${id}`, {
      method: 'DELETE',
    });
  }

  async getCompleteMeeting(id) {
    return this.request(`/api/meetings/${id}/complete`);
  }

  // Transcriptions
  async getTranscription(id) {
    return this.request(`/api/transcriptions/${id}`);
  }

  async getMeetingTranscription(meetingId) {
    return this.request(`/api/meetings/${meetingId}/transcription`);
  }

  async createTranscription(transcriptionData) {
    return this.request('/api/transcriptions', {
      method: 'POST',
      body: JSON.stringify(transcriptionData),
    });
  }

  // Meeting Minutes
  async getMeetingMinutes(id) {
    return this.request(`/api/meeting-minutes/${id}`);
  }

  async getMeetingMinutesByMeeting(meetingId) {
    return this.request(`/api/meetings/${meetingId}/minutes`);
  }

  async createMeetingMinutes(minutesData) {
    return this.request('/api/meeting-minutes', {
      method: 'POST',
      body: JSON.stringify(minutesData),
    });
  }

  // File downloads
  async downloadTranscript(meetingId) {
    const response = await fetch(`${this.baseURL}/api/meetings/${meetingId}/files/transcript`);
    if (!response.ok) {
      throw new Error('Failed to download transcript');
    }
    return response.blob();
  }

  async downloadMeetingMinutes(meetingId, format = 'docx') {
    const response = await fetch(`${this.baseURL}/api/meetings/${meetingId}/files/minutes?format=${format}`);
    if (!response.ok) {
      throw new Error('Failed to download meeting minutes');
    }
    return response.blob();
  }

  // Statistics
  async getStats() {
    return this.request('/api/stats');
  }

  // File management
  async getCleanupStatus() {
    return this.request('/api/cleanup-status');
  }

  async downloadMeetingZip(meetingId) {
    const response = await fetch(`${this.baseURL}/api/meetings/${meetingId}/zip`);
    if (!response.ok) {
      throw new Error('Failed to download zip file');
    }
    return response.blob();
  }

  // File upload
  async uploadFile(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const percentComplete = (event.loaded / event.total) * 100;
          onProgress(percentComplete);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid response format'));
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.status}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'));
      });

      xhr.open('POST', `${this.baseURL}/api/upload`);
      xhr.send(formData);
    });
  }
}

export const apiService = new ApiService();
