import React from 'react';
import { Chip } from '@mui/material';

const StatusChip = ({ status, size = 'small' }) => {
  const getStatusProps = (status) => {
    switch (status?.toLowerCase()) {
      case 'pending':
        return { label: 'Pending', color: 'default' };
      case 'processing':
        return { label: 'Processing', color: 'warning' };
      case 'completed':
        return { label: 'Completed', color: 'success' };
      case 'failed':
        return { label: 'Failed', color: 'error' };
      default:
        return { label: status || 'Unknown', color: 'default' };
    }
  };

  const { label, color } = getStatusProps(status);

  return <Chip label={label} color={color} size={size} />;
};

export default StatusChip;
