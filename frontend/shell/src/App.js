import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import VideoProcessing from './pages/VideoProcessing';
import Transcription from './pages/Transcription';
import MeetingMinutes from './pages/MeetingMinutes';
import MeetingsList from './pages/MeetingsList';
import MeetingDetail from './pages/MeetingDetail';

function App() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/video-processing" element={<VideoProcessing />} />
          <Route path="/transcription" element={<Transcription />} />
          <Route path="/meeting-minutes" element={<MeetingMinutes />} />
          <Route path="/meetings" element={<MeetingsList />} />
          <Route path="/meetings/:id" element={<MeetingDetail />} />
        </Routes>
      </Layout>
    </Box>
  );
}

export default App;
