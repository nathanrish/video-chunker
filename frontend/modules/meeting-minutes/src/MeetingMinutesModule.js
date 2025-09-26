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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Tabs,
  Tab,
  Badge,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Description as DocxIcon,
  Language as HtmlIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Assignment as AssignmentIcon,
  Group as GroupIcon,
  Timeline as TimelineIcon,
  BugReport as BugIcon,
  Link as LinkIcon,
  Gavel as GavelIcon,
} from '@mui/icons-material';
import { StatusChip, LoadingSpinner, ErrorBoundary } from '@video-meeting-minutes/shared';
import { formatDateTime } from '@video-meeting-minutes/shared';

const MeetingMinutesModule = ({ meetingId, apiService }) => {
  const [meetingMinutes, setMeetingMinutes] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (meetingId) {
      fetchMeetingMinutes();
    }
  }, [meetingId]);

  const fetchMeetingMinutes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.getMeetingMinutesByMeeting(meetingId);
      
      if (response.success) {
        setMeetingMinutes(response.data);
      } else {
        setError('Meeting minutes not found');
      }
    } catch (err) {
      setError('Failed to fetch meeting minutes: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (format) => {
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

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getRiskLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading meeting minutes..." />;
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (!meetingMinutes) {
    return (
      <Alert severity="info">
        No meeting minutes available for this meeting.
      </Alert>
    );
  }

  const { title, summary, artifacts, sprint_info, speakers } = meetingMinutes;

  return (
    <ErrorBoundary>
      <Box>
        <Typography variant="h4" gutterBottom>
          Meeting Minutes
        </Typography>

        <Grid container spacing={3}>
          {/* Header and Actions */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h5">
                    {title}
                  </Typography>
                  <Box>
                    <Button
                      variant="contained"
                      startIcon={<DocxIcon />}
                      onClick={() => handleDownload('docx')}
                      sx={{ mr: 1 }}
                    >
                      Download DOCX
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<HtmlIcon />}
                      onClick={() => handleDownload('html')}
                    >
                      Download HTML
                    </Button>
                  </Box>
                </Box>
                
                <Typography variant="body1" color="text.secondary" paragraph>
                  {summary}
                </Typography>
                
                <Box display="flex" gap={1} flexWrap="wrap">
                  <Chip
                    icon={<GroupIcon />}
                    label={`${speakers?.length || 0} Speakers`}
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    icon={<TimelineIcon />}
                    label={`${artifacts?.epics?.length || 0} Epics`}
                    color="secondary"
                    variant="outlined"
                  />
                  <Chip
                    icon={<AssignmentIcon />}
                    label={`${artifacts?.action_items?.length || 0} Action Items`}
                    color="info"
                    variant="outlined"
                  />
                  <Chip
                    icon={<WarningIcon />}
                    label={`${artifacts?.risks?.length || 0} Risks`}
                    color="warning"
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Tabs for different sections */}
          <Grid item xs={12}>
            <Card>
              <Tabs
                value={activeTab}
                onChange={(e, newValue) => setActiveTab(newValue)}
                variant="scrollable"
                scrollButtons="auto"
              >
                <Tab label="Summary" />
                <Tab label="Epics & Initiatives" />
                <Tab label="Action Items" />
                <Tab label="Risks" />
                <Tab label="Dependencies" />
                <Tab label="Decisions" />
                <Tab label="Sprint Info" />
              </Tabs>
            </Card>
          </Grid>

          {/* Tab Content */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                {/* Summary Tab */}
                {activeTab === 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Executive Summary
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {summary}
                    </Typography>
                    
                    {speakers && speakers.length > 0 && (
                      <Box mt={3}>
                        <Typography variant="h6" gutterBottom>
                          Participants
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {speakers.map((speaker, index) => (
                            <Chip
                              key={index}
                              label={speaker}
                              color="primary"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </Box>
                )}

                {/* Epics & Initiatives Tab */}
                {activeTab === 1 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Epics & Initiatives
                    </Typography>
                    {artifacts?.epics?.length > 0 ? (
                      <List>
                        {artifacts.epics.map((epic, index) => (
                          <ListItem key={index} divider>
                            <ListItemIcon>
                              <TimelineIcon color="primary" />
                            </ListItemIcon>
                            <ListItemText
                              primary={epic.title || epic.name}
                              secondary={epic.description}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography color="text.secondary">
                        No epics or initiatives identified.
                      </Typography>
                    )}
                  </Box>
                )}

                {/* Action Items Tab */}
                {activeTab === 2 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Action Items
                    </Typography>
                    {artifacts?.action_items?.length > 0 ? (
                      <List>
                        {artifacts.action_items.map((item, index) => (
                          <ListItem key={index} divider>
                            <ListItemIcon>
                              <AssignmentIcon color="primary" />
                            </ListItemIcon>
                            <ListItemText
                              primary={item.title || item.description}
                              secondary={
                                <Box>
                                  <Typography variant="body2" color="text.secondary">
                                    Owner: {item.owner || 'Unassigned'}
                                  </Typography>
                                  {item.due_date && (
                                    <Typography variant="body2" color="text.secondary">
                                      Due: {formatDateTime(item.due_date)}
                                    </Typography>
                                  )}
                                  {item.priority && (
                                    <Chip
                                      label={item.priority}
                                      color={getPriorityColor(item.priority)}
                                      size="small"
                                      sx={{ mt: 1 }}
                                    />
                                  )}
                                </Box>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography color="text.secondary">
                        No action items identified.
                      </Typography>
                    )}
                  </Box>
                )}

                {/* Risks Tab */}
                {activeTab === 3 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Risks & Issues
                    </Typography>
                    {artifacts?.risks?.length > 0 ? (
                      <List>
                        {artifacts.risks.map((risk, index) => (
                          <ListItem key={index} divider>
                            <ListItemIcon>
                              <WarningIcon color="warning" />
                            </ListItemIcon>
                            <ListItemText
                              primary={risk.title || risk.description}
                              secondary={
                                <Box>
                                  <Typography variant="body2" color="text.secondary">
                                    {risk.description}
                                  </Typography>
                                  <Box display="flex" gap={1} mt={1}>
                                    {risk.impact && (
                                      <Chip
                                        label={`Impact: ${risk.impact}`}
                                        color={getRiskLevelColor(risk.impact)}
                                        size="small"
                                      />
                                    )}
                                    {risk.probability && (
                                      <Chip
                                        label={`Probability: ${risk.probability}`}
                                        color={getRiskLevelColor(risk.probability)}
                                        size="small"
                                      />
                                    )}
                                  </Box>
                                </Box>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography color="text.secondary">
                        No risks identified.
                      </Typography>
                    )}
                  </Box>
                )}

                {/* Dependencies Tab */}
                {activeTab === 4 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Dependencies
                    </Typography>
                    {artifacts?.dependencies?.length > 0 ? (
                      <List>
                        {artifacts.dependencies.map((dep, index) => (
                          <ListItem key={index} divider>
                            <ListItemIcon>
                              <LinkIcon color="primary" />
                            </ListItemIcon>
                            <ListItemText
                              primary={dep.title || dep.description}
                              secondary={
                                <Box>
                                  <Typography variant="body2" color="text.secondary">
                                    {dep.description}
                                  </Typography>
                                  {dep.blocking && (
                                    <Chip
                                      label="Blocking"
                                      color="error"
                                      size="small"
                                      sx={{ mt: 1 }}
                                    />
                                  )}
                                </Box>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography color="text.secondary">
                        No dependencies identified.
                      </Typography>
                    )}
                  </Box>
                )}

                {/* Decisions Tab */}
                {activeTab === 5 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Decisions
                    </Typography>
                    {artifacts?.decisions?.length > 0 ? (
                      <List>
                        {artifacts.decisions.map((decision, index) => (
                          <ListItem key={index} divider>
                            <ListItemIcon>
                              <GavelIcon color="primary" />
                            </ListItemIcon>
                            <ListItemText
                              primary={decision.title || decision.description}
                              secondary={
                                <Box>
                                  <Typography variant="body2" color="text.secondary">
                                    {decision.description}
                                  </Typography>
                                  {decision.decision_maker && (
                                    <Typography variant="body2" color="text.secondary">
                                      Decision Maker: {decision.decision_maker}
                                    </Typography>
                                  )}
                                </Box>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography color="text.secondary">
                        No decisions recorded.
                      </Typography>
                    )}
                  </Box>
                )}

                {/* Sprint Info Tab */}
                {activeTab === 6 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Sprint Information
                    </Typography>
                    {sprint_info ? (
                      <Grid container spacing={2}>
                        {sprint_info.sprint_number && (
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">
                              Sprint Number
                            </Typography>
                            <Typography variant="body1">
                              {sprint_info.sprint_number}
                            </Typography>
                          </Grid>
                        )}
                        {sprint_info.sprint_goal && (
                          <Grid item xs={12}>
                            <Typography variant="body2" color="text.secondary">
                              Sprint Goal
                            </Typography>
                            <Typography variant="body1">
                              {sprint_info.sprint_goal}
                            </Typography>
                          </Grid>
                        )}
                        {sprint_info.velocity && (
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">
                              Velocity
                            </Typography>
                            <Typography variant="body1">
                              {sprint_info.velocity}
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    ) : (
                      <Typography color="text.secondary">
                        No sprint information available.
                      </Typography>
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </ErrorBoundary>
  );
};

export default MeetingMinutesModule;
