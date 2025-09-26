import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { MeetingMinutesModule } from '@video-meeting-minutes/meeting-minutes';
import { apiService } from '../services/api';

function MeetingMinutes() {
  const [meetings, setMeetings] = useState([]);
  const [selectedMeetingId, setSelectedMeetingId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const handleMeetingChange = (event) => {
    setSelectedMeetingId(event.target.value);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Meeting Minutes
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Select a meeting to view its generated meeting minutes and artifacts.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <FormControl fullWidth>
                <InputLabel>Select Meeting</InputLabel>
                <Select
                  value={selectedMeetingId}
                  onChange={handleMeetingChange}
                  label="Select Meeting"
                  disabled={loading}
                >
                  {meetings.map((meeting) => (
                    <MenuItem key={meeting.id} value={meeting.id}>
                      {meeting.title} - {meeting.date} ({meeting.status})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {error && (
          <Grid item xs={12}>
            <Alert severity="error">
              {error}
            </Alert>
          </Grid>
        )}

        {selectedMeetingId && (
          <Grid item xs={12}>
            <MeetingMinutesModule
              meetingId={selectedMeetingId}
              apiService={apiService}
            />
          </Grid>
        )}

        {!selectedMeetingId && !loading && (
          <Grid item xs={12}>
            <Alert severity="info">
              Please select a meeting to view its meeting minutes.
            </Alert>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default MeetingMinutes;
