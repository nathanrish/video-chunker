import React from 'react';
import { VideoProcessingModule } from '@video-meeting-minutes/video-processing';
import { apiService } from '../services/api';

function VideoProcessing() {
  const handleVideoProcessed = (meetingData) => {
    console.log('Video processed:', meetingData);
    // You could redirect to the meeting detail page or show a success message
  };

  return (
    <VideoProcessingModule
      onVideoProcessed={handleVideoProcessed}
      apiService={apiService}
    />
  );
}

export default VideoProcessing;
