import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  VideoLibrary as VideoIcon,
  Transcription as TranscriptionIcon,
  Description as MinutesIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const StatCard = ({ title, value, icon, color, onClick }) => (
  <Card 
    sx={{ 
      height: '100%', 
      cursor: onClick ? 'pointer' : 'default',
      '&:hover': onClick ? { boxShadow: 4 } : {}
    }}
    onClick={onClick}
  >
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography color="textSecondary" gutterBottom variant="h6">
            {title}
          </Typography>
          <Typography variant="h4" component="h2" color={color}>
            {value}
          </Typography>
        </Box>
        <Box color={color}>
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const QuickActionCard = ({ title, description, icon, color, onClick }) => (
  <Card 
    sx={{ 
      height: '100%', 
      cursor: 'pointer',
      '&:hover': { boxShadow: 4 }
    }}
    onClick={onClick}
  >
    <CardContent>
      <Box display="flex" flexDirection="column" alignItems="center" textAlign="center">
        <Box color={color} mb={2}>
          {icon}
        </Box>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Typography color="textSecondary">
          {description}
        </Typography>
      </Box>
    </CardContent>
  </Card>
);

function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalMeetings: 0,
    meetingsByStatus: {},
    totalDuration: 0,
    averageDuration: 0,
  });
  const [cleanupStatus, setCleanupStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
    fetchCleanupStatus();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await apiService.getStats();
      if (response.success) {
        setStats(response.data);
      } else {
        setError('Failed to fetch statistics');
      }
    } catch (err) {
      setError('Error fetching statistics: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCleanupStatus = async () => {
    try {
      const response = await apiService.getCleanupStatus();
      if (response.success) {
        setCleanupStatus(response.data);
      }
    } catch (err) {
      console.error('Error fetching cleanup status:', err);
    }
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Statistics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Meetings"
            value={stats.totalMeetings}
            icon={<VideoIcon sx={{ fontSize: 40 }} />}
            color="primary.main"
            onClick={() => navigate('/meetings')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed"
            value={stats.meetingsByStatus.completed || 0}
            icon={<MinutesIcon sx={{ fontSize: 40 }} />}
            color="success.main"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Processing"
            value={stats.meetingsByStatus.processing || 0}
            icon={<TranscriptionIcon sx={{ fontSize: 40 }} />}
            color="warning.main"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Duration"
            value={formatDuration(stats.totalDuration)}
            icon={<TrendingIcon sx={{ fontSize: 40 }} />}
            color="info.main"
          />
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom sx={{ mt: 3 }}>
            Quick Actions
          </Typography>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <QuickActionCard
            title="Process Video"
            description="Upload and process a new video for transcription"
            icon={<VideoIcon sx={{ fontSize: 48 }} />}
            color="primary.main"
            onClick={() => navigate('/video-processing')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <QuickActionCard
            title="View Transcriptions"
            description="Browse and manage video transcriptions"
            icon={<TranscriptionIcon sx={{ fontSize: 48 }} />}
            color="secondary.main"
            onClick={() => navigate('/transcription')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <QuickActionCard
            title="Meeting Minutes"
            description="Generate and view meeting minutes"
            icon={<MinutesIcon sx={{ fontSize: 48 }} />}
            color="success.main"
            onClick={() => navigate('/meeting-minutes')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <QuickActionCard
            title="All Meetings"
            description="View all meetings and their status"
            icon={<VideoIcon sx={{ fontSize: 48 }} />}
            color="info.main"
            onClick={() => navigate('/meetings')}
          />
        </Grid>

        {/* File Management Status */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom sx={{ mt: 3 }}>
            File Management
          </Typography>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                <Chip 
                  label="API Service" 
                  color="success" 
                  size="small" 
                />
                <Chip 
                  label="Transcription Service" 
                  color="success" 
                  size="small" 
                />
                <Chip 
                  label="Meeting Minutes Service" 
                  color="success" 
                  size="small" 
                />
                <Chip 
                  label="File Management Service" 
                  color="success" 
                  size="small" 
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cleanup Status
              </Typography>
              {cleanupStatus ? (
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Total Folders: {cleanupStatus.total_folders}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Old Folders (24h+): {cleanupStatus.old_folders}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Total Size: {cleanupStatus.total_size_mb} MB
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Next Cleanup: {cleanupStatus.next_cleanup}
                  </Typography>
                  <Chip 
                    label={`Auto-purge after ${cleanupStatus.cutoff_hours}h`}
                    color="info"
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Loading cleanup status...
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
