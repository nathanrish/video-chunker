import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Grid,
  Alert,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  VideoLibrary as VideoIcon,
  Upload as UploadIcon,
  PlayArrow as PlayIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { FileUpload, LoadingSpinner, ErrorBoundary } from '@video-meeting-minutes/shared';
import { formatFileSize, isVideoFile } from '@video-meeting-minutes/shared';

const VideoProcessingModule = ({ onVideoProcessed, apiService }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [meetingTitle, setMeetingTitle] = useState('');
  const [meetingDate, setMeetingDate] = useState(new Date());
  const [language, setLanguage] = useState('en');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    'Upload Video',
    'Meeting Details',
    'Process Video',
    'Complete',
  ];

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError(null);
    
    // Auto-fill meeting title from filename
    if (!meetingTitle) {
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
      setMeetingTitle(nameWithoutExt);
    }
  };

  const handleUpload = async (file, onProgress) => {
    try {
      setProcessing(true);
      setError(null);
      
      // Simulate upload progress
      for (let i = 0; i <= 100; i += 10) {
        onProgress(i);
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      // Here you would typically upload to your backend
      // For now, we'll just simulate success
      setSuccess('Video uploaded successfully!');
      setActiveStep(1);
    } catch (err) {
      setError('Upload failed: ' + err.message);
    } finally {
      setProcessing(false);
    }
  };

  const handleProcessVideo = async () => {
    try {
      setProcessing(true);
      setError(null);
      setActiveStep(2);
      
      // Create meeting record
      const meetingData = {
        title: meetingTitle,
        date: meetingDate.toISOString().split('T')[0],
        language: language,
        video_path: selectedFile.name, // In real app, this would be the uploaded path
        status: 'processing',
      };
      
      const response = await apiService.createMeeting(meetingData);
      
      if (response.success) {
        setSuccess('Video processing started successfully!');
        setActiveStep(3);
        
        if (onVideoProcessed) {
          onVideoProcessed(response.data);
        }
      } else {
        throw new Error(response.error || 'Failed to start video processing');
      }
    } catch (err) {
      setError('Processing failed: ' + err.message);
      setActiveStep(1);
    } finally {
      setProcessing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setMeetingTitle('');
    setMeetingDate(new Date());
    setLanguage('en');
    setError(null);
    setSuccess(null);
    setActiveStep(0);
  };

  const isStepValid = (step) => {
    switch (step) {
      case 0:
        return selectedFile && isVideoFile(selectedFile.name);
      case 1:
        return meetingTitle.trim() !== '';
      case 2:
        return true;
      default:
        return false;
    }
  };

  return (
    <ErrorBoundary>
      <Box>
        <Typography variant="h4" gutterBottom>
          Video Processing
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph>
          Upload a video file to start the transcription and meeting minutes generation process.
        </Typography>

        <Card>
          <CardContent>
            <Stepper activeStep={activeStep} orientation="vertical">
              <Step>
                <StepLabel>Upload Video File</StepLabel>
                <StepContent>
                  <Box mb={2}>
                    <FileUpload
                      accept="video/*"
                      maxSize={500 * 1024 * 1024} // 500MB
                      onFileSelect={handleFileSelect}
                      onUpload={handleUpload}
                      disabled={processing}
                    />
                  </Box>
                  
                  {selectedFile && (
                    <Box mt={2}>
                      <Chip
                        icon={<VideoIcon />}
                        label={`${selectedFile.name} (${formatFileSize(selectedFile.size)})`}
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                  )}
                  
                  <Box mt={2}>
                    <Button
                      variant="contained"
                      disabled={!isStepValid(0) || processing}
                      onClick={() => setActiveStep(1)}
                    >
                      Next
                    </Button>
                  </Box>
                </StepContent>
              </Step>

              <Step>
                <StepLabel>Meeting Details</StepLabel>
                <StepContent>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Meeting Title"
                        value={meetingTitle}
                        onChange={(e) => setMeetingTitle(e.target.value)}
                        required
                      />
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <LocalizationProvider dateAdapter={AdapterDateFns}>
                        <DatePicker
                          label="Meeting Date"
                          value={meetingDate}
                          onChange={(newValue) => setMeetingDate(newValue)}
                          renderInput={(params) => <TextField {...params} fullWidth />}
                        />
                      </LocalizationProvider>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Language"
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        select
                        SelectProps={{ native: true }}
                      >
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                        <option value="it">Italian</option>
                        <option value="pt">Portuguese</option>
                      </TextField>
                    </Grid>
                  </Grid>
                  
                  <Box mt={2}>
                    <Button
                      variant="contained"
                      disabled={!isStepValid(1)}
                      onClick={handleProcessVideo}
                      startIcon={processing ? <LoadingSpinner size={20} /> : <PlayIcon />}
                    >
                      {processing ? 'Processing...' : 'Start Processing'}
                    </Button>
                  </Box>
                </StepContent>
              </Step>

              <Step>
                <StepLabel>Processing Video</StepLabel>
                <StepContent>
                  {processing && (
                    <Box>
                      <Typography variant="body2" gutterBottom>
                        Processing your video...
                      </Typography>
                      <LinearProgress />
                    </Box>
                  )}
                </StepContent>
              </Step>

              <Step>
                <StepLabel>Complete</StepLabel>
                <StepContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <CheckIcon color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6">
                      Video processing completed!
                    </Typography>
                  </Box>
                  
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      <strong>File Management:</strong><br />
                      • Input video will be automatically deleted after processing<br />
                      • Output files will be zipped into a single archive<br />
                      • All files will be automatically purged after 24 hours
                    </Typography>
                  </Alert>
                  
                  <Button
                    variant="contained"
                    onClick={handleReset}
                    startIcon={<UploadIcon />}
                  >
                    Process Another Video
                  </Button>
                </StepContent>
              </Step>
            </Stepper>
          </CardContent>
        </Card>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mt: 2 }}>
            {success}
          </Alert>
        )}
      </Box>
    </ErrorBoundary>
  );
};

export default VideoProcessingModule;
