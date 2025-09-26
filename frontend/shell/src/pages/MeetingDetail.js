import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  Button,
  Chip,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Archive as ArchiveIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { StatusChip, LoadingSpinner } from '@video-meeting-minutes/shared';
import { formatDateTime, formatDuration } from '@video-meeting-minutes/shared';
import { TranscriptionModule } from '@video-meeting-minutes/transcription';
import { MeetingMinutesModule } from '@video-meeting-minutes/meeting-minutes';
import { apiService } from '../services/api';

function MeetingDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [meeting, setMeeting] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (id) {
      fetchMeeting();
    }
  }, [id]);

  const fetchMeeting = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.getCompleteMeeting(id);
      
      if (response.success) {
        setMeeting(response.data);
      } else {
        setError('Meeting not found');
      }
    } catch (err) {
      setError('Error fetching meeting: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadTranscript = async () => {
    try {
      const blob = await apiService.downloadTranscript(id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `transcript_${meeting.meeting.title}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download transcript: ' + err.message);
    }
  };

  const handleDownloadMinutes = async (format = 'docx') => {
    try {
      const blob = await apiService.downloadMeetingMinutes(id, format);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `meeting_minutes_${meeting.meeting.title}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download meeting minutes: ' + err.message);
    }
  };

  const handleDownloadZip = async () => {
    try {
      const blob = await apiService.downloadMeetingZip(id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `meeting_output_${meeting.meeting.title}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download zip file: ' + err.message);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading meeting details..." />;
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (!meeting) {
    return (
      <Alert severity="info">
        Meeting not found.
      </Alert>
    );
  }

  const { meeting: meetingData, transcription, minutes } = meeting;

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/meetings')}
          sx={{ mr: 2 }}
        >
          Back to Meetings
        </Button>
        <Typography variant="h4">
          {meetingData.title}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Meeting Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5">
                  Meeting Information
                </Typography>
                <Box>
                  <Button
                    variant="outlined"
                    startIcon={<EditIcon />}
                    onClick={() => navigate('/video-processing')}
                    sx={{ mr: 1 }}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<DownloadIcon />}
                    onClick={handleDownloadTranscript}
                    sx={{ mr: 1 }}
                  >
                    Download Transcript
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<DownloadIcon />}
                    onClick={() => handleDownloadMinutes('docx')}
                    sx={{ mr: 1 }}
                  >
                    Download Minutes
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<ArchiveIcon />}
                    onClick={handleDownloadZip}
                    color="secondary"
                  >
                    Download All (ZIP)
                  </Button>
                </Box>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <StatusChip status={meetingData.status} />
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Date
                  </Typography>
                  <Typography variant="body1">
                    {formatDateTime(meetingData.date)}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Language
                  </Typography>
                  <Typography variant="body1">
                    {meetingData.language?.toUpperCase() || 'N/A'}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Created
                  </Typography>
                  <Typography variant="body1">
                    {formatDateTime(meetingData.created_at)}
                  </Typography>
                </Grid>
                
                {transcription && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Duration
                    </Typography>
                    <Typography variant="body1">
                      {formatDuration(transcription.duration)}
                    </Typography>
                  </Grid>
                )}
                
                {meetingData.participants && meetingData.participants.length > 0 && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Participants
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap" mt={1}>
                      {meetingData.participants.map((participant, index) => (
                        <Chip
                          key={index}
                          label={participant}
                          color="primary"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Tabs for different views */}
        <Grid item xs={12}>
          <Card>
            <Tabs
              value={activeTab}
              onChange={(e, newValue) => setActiveTab(newValue)}
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab label="Overview" />
              <Tab label="Transcription" />
              <Tab label="Meeting Minutes" />
            </Tabs>
          </Card>
        </Grid>

        {/* Tab Content */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              {/* Overview Tab */}
              {activeTab === 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Meeting Overview
                  </Typography>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" gutterBottom>
                        Processing Status
                      </Typography>
                      <Box mb={2}>
                        <StatusChip status={meetingData.status} />
                      </Box>
                      
                      {meetingData.processing_step && (
                        <Typography variant="body2" color="text.secondary">
                          Current Step: {meetingData.processing_step}
                        </Typography>
                      )}
                      
                      {meetingData.error_message && (
                        <Alert severity="error" sx={{ mt: 2 }}>
                          {meetingData.error_message}
                        </Alert>
                      )}
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" gutterBottom>
                        Available Files
                      </Typography>
                      <Box display="flex" flexDirection="column" gap={1}>
                        <Button
                          variant="outlined"
                          startIcon={<DownloadIcon />}
                          onClick={handleDownloadTranscript}
                          disabled={!transcription}
                        >
                          Transcript ({transcription ? 'Available' : 'Not Available'})
                        </Button>
                        <Button
                          variant="outlined"
                          startIcon={<DownloadIcon />}
                          onClick={() => handleDownloadMinutes('docx')}
                          disabled={!minutes}
                        >
                          Meeting Minutes DOCX ({minutes ? 'Available' : 'Not Available'})
                        </Button>
                        <Button
                          variant="outlined"
                          startIcon={<DownloadIcon />}
                          onClick={() => handleDownloadMinutes('html')}
                          disabled={!minutes}
                        >
                          Meeting Minutes HTML ({minutes ? 'Available' : 'Not Available'})
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {/* Transcription Tab */}
              {activeTab === 1 && (
                <Box>
                  {transcription ? (
                    <TranscriptionModule
                      meetingId={id}
                      apiService={apiService}
                    />
                  ) : (
                    <Alert severity="info">
                      No transcription available for this meeting.
                    </Alert>
                  )}
                </Box>
              )}

              {/* Meeting Minutes Tab */}
              {activeTab === 2 && (
                <Box>
                  {minutes ? (
                    <MeetingMinutesModule
                      meetingId={id}
                      apiService={apiService}
                    />
                  ) : (
                    <Alert severity="info">
                      No meeting minutes available for this meeting.
                    </Alert>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default MeetingDetail;
