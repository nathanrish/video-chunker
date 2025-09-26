# File Management Features

This document describes the new file management features added to the Video-to-Meeting-Minutes system.

## 🗂️ Overview

The system now includes automatic file management features to:
1. **Delete input files** after successful processing
2. **Zip output files** into a single archive
3. **Auto-purge files** after 24 hours to save disk space

## 🔧 Backend Features

### File Management Service Enhancements

#### New Methods Added to `FileManagementService`:

1. **`delete_input_file(video_path)`**
   - Safely deletes input video files after processing
   - Only deletes files from the `input/` directory for safety
   - Returns success/error status

2. **`zip_output_folder(output_folder, meeting_title)`**
   - Creates a zip archive containing all output files
   - Uses meeting title for zip filename
   - Returns zip file path and metadata

3. **`_cleanup_old_files()`** (Background Thread)
   - Runs every hour to check for old files
   - Deletes output folders older than 24 hours
   - Runs as a daemon thread

4. **`get_cleanup_status()`**
   - Returns statistics about file cleanup
   - Shows total folders, old folders, disk usage
   - Provides cleanup schedule information

#### New API Endpoints:

- `POST /delete-input-file` - Delete input video file
- `POST /zip-output-folder` - Create zip archive of output
- `GET /cleanup-status` - Get cleanup statistics

### Orchestrator Updates

The orchestrator now includes additional steps in the workflow:

1. **Step 10: Zip Output Folder**
   - Creates zip archive after all files are generated
   - Includes all output files in a single download

2. **Step 11: Delete Input File**
   - Removes original video file from input directory
   - Only executes if video was successfully copied to output

## 🎨 Frontend Features

### Dashboard Enhancements

- **File Management Status Section**
  - Shows total folders and old folders count
  - Displays disk usage in MB
  - Shows next cleanup schedule
  - Auto-purge status indicator

### Meeting Management

#### New Download Options:
- **ZIP Download Button** (Archive icon)
  - Downloads all meeting files as a single zip
  - Available in meetings list and meeting detail pages
  - Includes transcript, minutes, and all generated files

#### Enhanced UI:
- **File Management Information**
  - Clear messaging about automatic file cleanup
  - User notification about 24-hour purge policy
  - Status indicators for file management operations

### API Service Updates

New methods added to `apiService`:
- `getCleanupStatus()` - Fetch cleanup statistics
- `downloadMeetingZip(meetingId)` - Download zip archive

## 📁 File Structure Changes

### Input Directory
```
input/
├── video1.mp4          # Will be deleted after processing
├── video2.mp4          # Will be deleted after processing
└── ...
```

### Output Directory
```
output/
├── 2024-01-15_Meeting_Title/
│   ├── transcript.txt
│   ├── meeting_minutes.docx
│   ├── meeting_minutes.html
│   ├── original_video.mp4
│   ├── workflow_summary.json
│   └── Meeting_Title_output.zip    # New: Zipped archive
└── ...
```

## ⚙️ Configuration

### Environment Variables

No new environment variables required. The system uses:
- `input/` directory for input files (configurable)
- `output/` directory for output files (configurable)
- 24-hour cleanup threshold (hardcoded)

### Service Configuration

The file management service can be configured with:
```python
FileManagementService(
    base_output_dir="./output",
    input_dir="./input"
)
```

## 🔄 Workflow Changes

### Complete Processing Workflow

1. **Video Upload** → Input directory
2. **Transcription** → Generate transcript
3. **Meeting Minutes** → Generate minutes
4. **File Organization** → Create dated folder
5. **File Saving** → Save all outputs
6. **Video Copy** → Copy original to output
7. **Workflow Summary** → Create summary JSON
8. **ZIP Creation** → Create zip archive ✨ **NEW**
9. **Input Deletion** → Delete original video ✨ **NEW**
10. **Background Cleanup** → Auto-purge after 24h ✨ **NEW**

## 🛡️ Safety Features

### Input File Deletion Safety
- Only deletes files from the `input/` directory
- Prevents accidental deletion of files outside input folder
- Validates file path before deletion
- Logs all deletion operations

### Cleanup Safety
- Only deletes folders older than 24 hours
- Preserves recent processing results
- Runs in background thread to avoid blocking
- Comprehensive error handling and logging

## 📊 Monitoring

### Cleanup Status Dashboard
- **Total Folders**: Count of all output folders
- **Old Folders**: Count of folders eligible for cleanup
- **Total Size**: Disk usage in MB
- **Next Cleanup**: Schedule information
- **Auto-purge Policy**: 24-hour threshold display

### Logging
- All file operations are logged
- Cleanup operations are tracked
- Error conditions are reported
- Performance metrics are recorded

## 🚀 Benefits

### Storage Management
- **Automatic cleanup** prevents disk space issues
- **ZIP compression** reduces storage requirements
- **Input file deletion** frees up space immediately

### User Experience
- **Single download** option for all files
- **Clear messaging** about file management
- **Status visibility** for cleanup operations

### System Maintenance
- **Automated cleanup** reduces manual maintenance
- **Background processing** doesn't block user operations
- **Configurable thresholds** for different environments

## 🔧 Troubleshooting

### Common Issues

1. **Input file not deleted**
   - Check if file is in `input/` directory
   - Verify file permissions
   - Check service logs for errors

2. **ZIP file not created**
   - Verify output folder exists
   - Check disk space availability
   - Review file permissions

3. **Cleanup not working**
   - Check background thread status
   - Verify folder timestamps
   - Review cleanup logs

### Debug Commands

```bash
# Check cleanup status
curl http://localhost:5003/cleanup-status

# Check file management service health
curl http://localhost:5003/health

# View service logs
tail -f logs/file_management.log
```

## 📈 Performance Impact

### Positive Impacts
- **Reduced disk usage** through automatic cleanup
- **Faster downloads** with ZIP compression
- **Better organization** with single-file downloads

### Considerations
- **Background thread** uses minimal resources
- **ZIP creation** adds processing time
- **File deletion** is immediate and irreversible

## 🔮 Future Enhancements

### Planned Features
- **Configurable cleanup intervals** (not just 24 hours)
- **Selective file retention** (keep important files longer)
- **Cloud storage integration** for long-term archiving
- **User preferences** for file management settings
- **Advanced compression** options for ZIP files

### Monitoring Improvements
- **Real-time cleanup status** updates
- **Disk usage alerts** when approaching limits
- **Cleanup history** and statistics
- **Performance metrics** for file operations

## 📝 Migration Notes

### For Existing Installations
1. **No breaking changes** - existing functionality preserved
2. **New features are opt-in** - gradual adoption possible
3. **Backward compatibility** maintained
4. **Configuration updates** not required

### For New Installations
1. **All features enabled** by default
2. **Automatic cleanup** starts immediately
3. **ZIP creation** happens for all new meetings
4. **Input deletion** occurs after successful processing

This file management system provides a robust, automated solution for handling the lifecycle of video processing files while maintaining system performance and user convenience.
