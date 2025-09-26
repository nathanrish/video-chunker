import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import App from '../App';

// Mock the micro frontend modules
jest.mock('@video-meeting-minutes/video-processing', () => ({
  VideoProcessingModule: () => <div data-testid="video-processing-module">Video Processing Module</div>
}));

jest.mock('@video-meeting-minutes/transcription', () => ({
  TranscriptionModule: () => <div data-testid="transcription-module">Transcription Module</div>
}));

jest.mock('@video-meeting-minutes/meeting-minutes', () => ({
  MeetingMinutesModule: () => <div data-testid="meeting-minutes-module">Meeting Minutes Module</div>
}));

const theme = createTheme();

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        {component}
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('App Component', () => {
  test('renders without crashing', () => {
    renderWithProviders(<App />);
    expect(screen.getByText('Video to Meeting Minutes')).toBeInTheDocument();
  });

  test('renders navigation menu', () => {
    renderWithProviders(<App />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Video Processing')).toBeInTheDocument();
    expect(screen.getByText('Transcriptions')).toBeInTheDocument();
    expect(screen.getByText('Meeting Minutes')).toBeInTheDocument();
    expect(screen.getByText('Meetings')).toBeInTheDocument();
  });

  test('renders dashboard by default', () => {
    renderWithProviders(<App />);
    expect(screen.getByText('Welcome to Video to Meeting Minutes')).toBeInTheDocument();
  });
});
