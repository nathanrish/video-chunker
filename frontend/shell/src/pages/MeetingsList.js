import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  IconButton,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Archive as ArchiveIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { DataTable, StatusChip, LoadingSpinner } from '@video-meeting-minutes/shared';
import { formatDateTime, formatDuration } from '@video-meeting-minutes/shared';
import { apiService } from '../services/api';

function MeetingsList() {
  const navigate = useNavigate();
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [meetingToDelete, setMeetingToDelete] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.getMeetings({ limit: 100 });
      
      if (response.success) {
        setMeetings(response.data);
      } else {
        setError('Failed to fetch meetings');
      }
    } catch (err) {
      setError('Error fetching meetings: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleView = (meeting) => {
    navigate(`/meetings/${meeting.id}`);
  };

  const handleEdit = (meeting) => {
    // Implement edit functionality
    console.log('Edit meeting:', meeting);
  };

  const handleDelete = (meeting) => {
    setMeetingToDelete(meeting);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!meetingToDelete) return;

    try {
      const response = await apiService.deleteMeeting(meetingToDelete.id);
      
      if (response.success) {
        setMeetings(meetings.filter(m => m.id !== meetingToDelete.id));
        setDeleteDialogOpen(false);
        setMeetingToDelete(null);
      } else {
        setError('Failed to delete meeting');
      }
    } catch (err) {
      setError('Error deleting meeting: ' + err.message);
    }
  };

  const handleDownloadTranscript = async (meetingId) => {
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

  const handleDownloadMinutes = async (meetingId, format = 'docx') => {
    try {
      const blob = await apiService.downloadMeetingMinutes(meetingId, format);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `meeting_minutes_${meetingId}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download meeting minutes: ' + err.message);
    }
  };

  const handleDownloadZip = async (meetingId) => {
    try {
      const blob = await apiService.downloadMeetingZip(meetingId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `meeting_output_${meetingId}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download zip file: ' + err.message);
    }
  };

  const columns = [
    {
      field: 'title',
      headerName: 'Title',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'date',
      headerName: 'Date',
      width: 120,
      renderCell: (params) => formatDateTime(params.value),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => <StatusChip status={params.value} />,
    },
    {
      field: 'language',
      headerName: 'Language',
      width: 100,
      renderCell: (params) => params.value?.toUpperCase() || 'N/A',
    },
    {
      field: 'created_at',
      headerName: 'Created',
      width: 150,
      renderCell: (params) => formatDateTime(params.value),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 250,
      renderCell: (params) => (
        <Box>
          <IconButton
            size="small"
            onClick={() => handleView(params.row)}
            title="View Details"
          >
            <ViewIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => handleEdit(params.row)}
            title="Edit"
          >
            <EditIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => handleDownloadTranscript(params.row.id)}
            title="Download Transcript"
          >
            <DownloadIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => handleDownloadZip(params.row.id)}
            title="Download All Files (ZIP)"
          >
            <ArchiveIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => handleDelete(params.row)}
            title="Delete"
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      ),
    },
  ];

  const filteredMeetings = meetings.filter(meeting =>
    meeting.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    meeting.date.includes(searchTerm)
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Meetings
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/video-processing')}
        >
          Process New Video
        </Button>
      </Box>

      <Card>
        <CardContent>
          <Grid container spacing={2} alignItems="center" mb={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Search meetings"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box display="flex" gap={1}>
                <Chip
                  label={`Total: ${meetings.length}`}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={`Completed: ${meetings.filter(m => m.status === 'completed').length}`}
                  color="success"
                  variant="outlined"
                />
                <Chip
                  label={`Processing: ${meetings.filter(m => m.status === 'processing').length}`}
                  color="warning"
                  variant="outlined"
                />
              </Box>
            </Grid>
          </Grid>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <DataTable
            rows={filteredMeetings}
            columns={columns}
            loading={loading}
            onView={handleView}
            onEdit={handleEdit}
            onDelete={handleDelete}
            pageSize={10}
            getRowId={(row) => row.id}
          />
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Meeting</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the meeting "{meetingToDelete?.title}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={confirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default MeetingsList;
