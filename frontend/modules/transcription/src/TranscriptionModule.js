import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
  Search as SearchIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
} from '@mui/icons-material';
import { StatusChip, LoadingSpinner, ErrorBoundary, DataTable } from '@video-meeting-minutes/shared';
import { formatDateTime, formatDuration } from '@video-meeting-minutes/shared';

const TranscriptionModule = ({ meetingId, apiService }) => {
  const [transcription, setTranscription] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredSegments, setFilteredSegments] = useState([]);
  const [playingSegment, setPlayingSegment] = useState(null);

  useEffect(() => {
    if (meetingId) {
      fetchTranscription();
    }
  }, [meetingId]);

  useEffect(() => {
    if (transcription?.segments) {
      filterSegments();
    }
  }, [transcription, searchTerm]);

  const fetchTranscription = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.getMeetingTranscription(meetingId);
      
      if (response.success) {
        setTranscription(response.data);
      } else {
        setError('Transcription not found');
      }
    } catch (err) {
      setError('Failed to fetch transcription: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const filterSegments = () => {
    if (!transcription?.segments) return;
    
    const filtered = transcription.segments.filter(segment =>
      segment.text.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredSegments(filtered);
  };

  const handleDownloadTranscript = async () => {
    try {
      const blob = await apiService.downloadTranscript(meetingId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `transcript_${meetingId}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download transcript: ' + err.message);
    }
  };

  const handleCopyText = (text) => {
    navigator.clipboard.writeText(text);
  };

  const handlePlaySegment = (segment) => {
    setPlayingSegment(playingSegment === segment.id ? null : segment.id);
  };

  const formatTimestamp = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const columns = [
    {
      field: 'start',
      headerName: 'Start Time',
      width: 100,
      renderCell: (params) => formatTimestamp(params.value),
    },
    {
      field: 'end',
      headerName: 'End Time',
      width: 100,
      renderCell: (params) => formatTimestamp(params.value),
    },
    {
      field: 'text',
      headerName: 'Text',
      flex: 1,
      minWidth: 300,
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Play/Pause">
            <IconButton
              size="small"
              onClick={() => handlePlaySegment(params.row)}
            >
              {playingSegment === params.row.id ? <PauseIcon /> : <PlayIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Copy Text">
            <IconButton
              size="small"
              onClick={() => handleCopyText(params.row.text)}
            >
              <CopyIcon />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  if (loading) {
    return <LoadingSpinner message="Loading transcription..." />;
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (!transcription) {
    return (
      <Alert severity="info">
        No transcription available for this meeting.
      </Alert>
    );
  }

  return (
    <ErrorBoundary>
      <Box>
        <Typography variant="h4" gutterBottom>
          Transcription Details
        </Typography>

        <Grid container spacing={3}>
          {/* Transcription Info */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    Transcription Information
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<DownloadIcon />}
                    onClick={handleDownloadTranscript}
                  >
                    Download Transcript
                  </Button>
                </Box>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Language
                    </Typography>
                    <Typography variant="body1">
                      {transcription.language?.toUpperCase() || 'Unknown'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Duration
                    </Typography>
                    <Typography variant="body1">
                      {formatDuration(transcription.duration)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Segments
                    </Typography>
                    <Typography variant="body1">
                      {transcription.segments?.length || 0}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Created
                    </Typography>
                    <Typography variant="body1">
                      {formatDateTime(transcription.created_at)}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Search and Filter */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <TextField
                    fullWidth
                    label="Search in transcription"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                      startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                    }}
                  />
                  {searchTerm && (
                    <Chip
                      label={`${filteredSegments.length} results`}
                      color="primary"
                      variant="outlined"
                    />
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Full Text */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    Full Transcription
                  </Typography>
                  <Button
                    startIcon={<CopyIcon />}
                    onClick={() => handleCopyText(transcription.text)}
                  >
                    Copy All
                  </Button>
                </Box>
                
                <Box
                  sx={{
                    maxHeight: 300,
                    overflow: 'auto',
                    p: 2,
                    backgroundColor: 'grey.50',
                    borderRadius: 1,
                    border: '1px solid',
                    borderColor: 'grey.300',
                  }}
                >
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {transcription.text}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Segments Table */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Segments ({filteredSegments.length})
                </Typography>
                
                <DataTable
                  rows={filteredSegments}
                  columns={columns}
                  loading={loading}
                  pageSize={10}
                  getRowId={(row) => row.id || row.start}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Segments Accordion View */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Segments (Accordion View)
                </Typography>
                
                {filteredSegments.map((segment, index) => (
                  <Accordion key={segment.id || index}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Box display="flex" alignItems="center" width="100%">
                        <Typography variant="body2" sx={{ mr: 2, minWidth: 80 }}>
                          {formatTimestamp(segment.start)} - {formatTimestamp(segment.end)}
                        </Typography>
                        <Typography variant="body2" sx={{ flexGrow: 1, mr: 2 }}>
                          {segment.text.substring(0, 100)}
                          {segment.text.length > 100 && '...'}
                        </Typography>
                        <Box>
                          <Tooltip title="Play/Pause">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handlePlaySegment(segment);
                              }}
                            >
                              {playingSegment === segment.id ? <PauseIcon /> : <PlayIcon />}
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Copy Text">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleCopyText(segment.text);
                              }}
                            >
                              <CopyIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                        {segment.text}
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </ErrorBoundary>
  );
};

export default TranscriptionModule;
