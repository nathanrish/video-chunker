import React from 'react';
import {
  DataGrid,
  GridToolbar,
  GridActionsCellItem,
} from '@mui/x-data-grid';
import { Edit as EditIcon, Delete as DeleteIcon, Visibility as ViewIcon } from '@mui/icons-material';

const DataTable = ({
  rows = [],
  columns = [],
  loading = false,
  onEdit,
  onDelete,
  onView,
  pageSize = 10,
  pageSizeOptions = [5, 10, 25, 50],
  ...props
}) => {
  const actionColumns = [];

  if (onView) {
    actionColumns.push({
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 120,
      getActions: (params) => [
        <GridActionsCellItem
          icon={<ViewIcon />}
          label="View"
          onClick={() => onView(params.row)}
        />,
        ...(onEdit ? [
          <GridActionsCellItem
            icon={<EditIcon />}
            label="Edit"
            onClick={() => onEdit(params.row)}
          />
        ] : []),
        ...(onDelete ? [
          <GridActionsCellItem
            icon={<DeleteIcon />}
            label="Delete"
            onClick={() => onDelete(params.row)}
          />
        ] : []),
      ],
    });
  }

  const allColumns = [...columns, ...actionColumns];

  return (
    <div style={{ height: 400, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={allColumns}
        loading={loading}
        pageSize={pageSize}
        pageSizeOptions={pageSizeOptions}
        disableSelectionOnClick
        components={{
          Toolbar: GridToolbar,
        }}
        componentsProps={{
          toolbar: {
            showQuickFilter: true,
            quickFilterProps: { debounceMs: 500 },
          },
        }}
        {...props}
      />
    </div>
  );
};

export default DataTable;
