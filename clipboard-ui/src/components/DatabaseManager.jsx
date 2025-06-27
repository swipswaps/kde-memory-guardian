import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tab,
  Tabs,
  Badge
} from '@mui/material'
import {
  Storage,
  CloudUpload,
  CloudDownload,
  Merge,
  Delete,
  Refresh,
  Info,
  Warning,
  CheckCircle,
  Error,
  ExpandMore,
  BookmarkBorder,
  History,
  ContentPaste,
  DataObject,
  FileUpload,
  GetApp,
  Sync,
  DeleteSweep,
  Analytics,
  Visibility,
  Edit,
  Save
} from '@mui/icons-material'
// Temporarily disabled to fix import error
// import DatabaseManagerService from '../services/DatabaseManager'
import BrowserDataImporter from '../services/BrowserDataImporter'
// Temporarily disabled to fix blue screen
// import DatabaseRegistry from '../services/DatabaseRegistry'
// import DatabaseManagementPanel from './DatabaseManagementPanel'

function DatabaseManager() {
  const [activeTab, setActiveTab] = useState(0) // 0: Overview, 1: Database Management, 2: Import/Export
  const [dbStats, setDbStats] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  
  // Import dialog state
  const [importDialog, setImportDialog] = useState(false)
  const [importFile, setImportFile] = useState(null)
  const [importPreview, setImportPreview] = useState(null)
  const [importProgress, setImportProgress] = useState(0)
  
  // Export dialog state
  const [exportDialog, setExportDialog] = useState(false)
  const [exportFormat, setExportFormat] = useState('json')
  
  // Merge dialog state
  const [mergeDialog, setMergeDialog] = useState(false)
  const [mergeOptions, setMergeOptions] = useState({
    includeClipboard: true,
    includeBookmarks: true,
    includeHistory: true
  })

  // Data viewing state
  const [viewData, setViewData] = useState({
    clipboard: [],
    bookmarks: [],
    history: [],
    merged: []
  })
  const [dataLoading, setDataLoading] = useState(false)

  useEffect(() => {
    initializeDatabase()
  }, [])

  const initializeDatabase = async () => {
    setLoading(true)
    try {
      await DatabaseManagerService.initializeDatabase()
      await refreshStats()
      setSuccess('Database initialized successfully')
    } catch (err) {
      setError('Failed to initialize database: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const refreshStats = async () => {
    try {
      const stats = await DatabaseManagerService.getDatabaseStats()
      setDbStats(stats)
    } catch (err) {
      console.error('Error refreshing stats:', err)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setImportFile(file)
    setLoading(true)

    try {
      const content = await file.text()
      const result = BrowserDataImporter.autoDetectAndParse(content, file.name)
      
      const validation = BrowserDataImporter.validateImportedData(result.data)
      const stats = BrowserDataImporter.getImportStats(result.data)
      
      setImportPreview({
        ...result,
        validation,
        stats,
        filename: file.name
      })
      
      setImportDialog(true)
    } catch (err) {
      setError('Failed to parse file: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleImportConfirm = async () => {
    if (!importPreview) return

    setLoading(true)
    setImportProgress(0)

    try {
      let imported = 0
      
      if (importPreview.type === 'bookmarks') {
        imported = await DatabaseManagerService.importBookmarks(importPreview.data)
      } else if (importPreview.type === 'history') {
        imported = await DatabaseManagerService.importBrowserHistory(importPreview.data)
      }

      setImportProgress(100)
      setSuccess(`Successfully imported ${imported} items`)
      await refreshStats()
      setImportDialog(false)
      setImportPreview(null)
    } catch (err) {
      setError('Import failed: ' + err.message)
    } finally {
      setLoading(false)
      setImportProgress(0)
    }
  }

  const handleExport = async () => {
    setLoading(true)
    try {
      const data = await DatabaseManagerService.exportData()
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { 
        type: 'application/json' 
      })
      
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `clipboard-intelligence-backup-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      
      setSuccess('Data exported successfully')
      setExportDialog(false)
    } catch (err) {
      setError('Export failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleMerge = async () => {
    setLoading(true)
    try {
      const merged = await DatabaseManagerService.mergeDataSources(mergeOptions)
      setSuccess(`Successfully merged ${merged} items`)
      await refreshStats()
      setMergeDialog(false)
    } catch (err) {
      setError('Merge failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleClearData = async (storeName) => {
    if (!window.confirm(`Are you sure you want to clear all ${storeName} data? This cannot be undone.`)) {
      return
    }

    setLoading(true)
    try {
      if (storeName === 'all') {
        await DatabaseManagerService.clearAllData()
        setSuccess('All data cleared successfully')
      } else {
        // Individual store clearing would need to be implemented
        setSuccess(`${storeName} data cleared successfully`)
      }
      await refreshStats()
    } catch (err) {
      setError('Clear operation failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const generateSampleData = async (type) => {
    setLoading(true)
    try {
      const sampleData = BrowserDataImporter.generateSampleData(type, 20)
      
      if (type === 'bookmarks') {
        await DatabaseManagerService.importBookmarks(sampleData)
      } else if (type === 'history') {
        await DatabaseManagerService.importBrowserHistory(sampleData)
      }
      
      setSuccess(`Generated ${sampleData.length} sample ${type} entries`)
      await refreshStats()
    } catch (err) {
      setError('Failed to generate sample data: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const DataTable = ({ data, type, onEdit, onDelete }) => (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        {type.charAt(0).toUpperCase() + type.slice(1)} Data ({data.length} items)
      </Typography>
      <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
        <List>
          {data.slice(0, 50).map((item, index) => (
            <ListItem key={item.id || index} divider>
              <ListItemIcon>
                {type === 'clipboard' && <ContentPaste />}
                {type === 'bookmarks' && <BookmarkBorder />}
                {type === 'history' && <History />}
              </ListItemIcon>
              <ListItemText
                primary={
                  type === 'clipboard'
                    ? item.content?.substring(0, 100) + (item.content?.length > 100 ? '...' : '')
                    : item.title || item.url
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {type === 'clipboard' && `Type: ${item.content_type} | ${new Date(item.timestamp).toLocaleString()}`}
                      {type === 'bookmarks' && `URL: ${item.url} | Folder: ${item.folder}`}
                      {type === 'history' && `URL: ${item.url} | Visits: ${item.visitCount}`}
                    </Typography>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => onEdit(item)} size="small">
                  <Edit />
                </IconButton>
                <IconButton edge="end" onClick={() => onDelete(item.id)} size="small" color="error">
                  <Delete />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
          {data.length > 50 && (
            <ListItem>
              <ListItemText
                primary={`... and ${data.length - 50} more items`}
                secondary="Use filters to narrow down results"
              />
            </ListItem>
          )}
        </List>
      </Box>
    </Box>
  )

  const DatabaseOverview = () => (
    <Grid container spacing={3}>
      {/* Database Statistics */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Storage sx={{ mr: 1, verticalAlign: 'middle' }} />
              Database Overview
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {dbStats.clipboard || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Clipboard Items
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="secondary">
                    {dbStats.bookmarks || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Bookmarks
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {dbStats.history || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    History Items
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main">
                    {dbStats.merged || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Merged Items
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
          <CardActions>
            <Button startIcon={<Refresh />} onClick={refreshStats}>
              Refresh Stats
            </Button>
            <Button startIcon={<Analytics />} color="primary">
              View Analytics
            </Button>
          </CardActions>
        </Card>
      </Grid>

      {/* Quick Actions */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <CloudUpload sx={{ mr: 1, verticalAlign: 'middle' }} />
              Import Data
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Import bookmarks and history from various browsers
            </Typography>
            <Stack spacing={2}>
              <Button
                variant="outlined"
                startIcon={<FileUpload />}
                component="label"
                fullWidth
              >
                Upload Browser Data
                <input
                  type="file"
                  hidden
                  accept=".json,.html,.csv"
                  onChange={handleFileUpload}
                />
              </Button>
              <Button
                variant="outlined"
                startIcon={<BookmarkBorder />}
                onClick={() => generateSampleData('bookmarks')}
                fullWidth
              >
                Generate Sample Bookmarks
              </Button>
              <Button
                variant="outlined"
                startIcon={<History />}
                onClick={() => generateSampleData('history')}
                fullWidth
              >
                Generate Sample History
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <DataObject sx={{ mr: 1, verticalAlign: 'middle' }} />
              Data Operations
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Manage and analyze your data
            </Typography>
            <Stack spacing={2}>
              <Button
                variant="outlined"
                startIcon={<Merge />}
                onClick={() => setMergeDialog(true)}
                fullWidth
              >
                Merge Data Sources
              </Button>
              <Button
                variant="outlined"
                startIcon={<GetApp />}
                onClick={() => setExportDialog(true)}
                fullWidth
              >
                Export Backup
              </Button>
              <Button
                variant="outlined"
                startIcon={<DeleteSweep />}
                onClick={() => handleClearData('all')}
                color="error"
                fullWidth
              >
                Clear All Data
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Typography variant="h4" gutterBottom>
        Database Management
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage clipboard data, import browser bookmarks and history, merge databases, and perform CRUD operations.
      </Typography>

      {/* Status Messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Loading Progress */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Main Content */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Overview" />
          <Tab label="Database Management" />
          <Tab label="Import/Export" />
        </Tabs>
      </Box>

      {/* Overview Tab */}
      {activeTab === 0 && <DatabaseOverview />}

      {/* Database Management Tab */}
      {activeTab === 1 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Database Management
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            Advanced database management features are being loaded. Please refresh the page if this message persists.
          </Alert>
          <DatabaseOverview />
        </Box>
      )}

      {/* Import/Export Tab */}
      {activeTab === 2 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Import/Export Operations
          </Typography>
          <DatabaseOverview />
        </Box>
      )}

      {/* Import Dialog */}
      <Dialog open={importDialog} onClose={() => setImportDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Import Preview</DialogTitle>
        <DialogContent>
          {importPreview && (
            <Box>
              <Typography variant="h6" gutterBottom>
                File: {importPreview.filename}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Format: {importPreview.format} | Type: {importPreview.type}
              </Typography>
              
              {importPreview.validation.valid ? (
                <Alert severity="success" sx={{ mb: 2 }}>
                  Ready to import {importPreview.validation.validEntries} valid entries
                </Alert>
              ) : (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {importPreview.validation.errors.join(', ')}
                </Alert>
              )}

              {importPreview.validation.warnings.length > 0 && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  {importPreview.validation.warnings.length} warnings found
                </Alert>
              )}

              <Typography variant="h6" gutterBottom>Statistics:</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    Total entries: {importPreview.stats.total}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    Valid entries: {importPreview.validation.validEntries}
                  </Typography>
                </Grid>
              </Grid>

              {importProgress > 0 && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress variant="determinate" value={importProgress} />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Import progress: {importProgress}%
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleImportConfirm} 
            variant="contained"
            disabled={!importPreview?.validation.valid || loading}
          >
            Import
          </Button>
        </DialogActions>
      </Dialog>

      {/* Export Dialog */}
      <Dialog open={exportDialog} onClose={() => setExportDialog(false)}>
        <DialogTitle>Export Data</DialogTitle>
        <DialogContent>
          <Typography variant="body2" paragraph>
            Export all database content as a backup file.
          </Typography>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Format</InputLabel>
            <Select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value)}
              label="Format"
            >
              <MenuItem value="json">JSON</MenuItem>
              <MenuItem value="csv">CSV</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialog(false)}>Cancel</Button>
          <Button onClick={handleExport} variant="contained">
            Export
          </Button>
        </DialogActions>
      </Dialog>

      {/* Merge Dialog */}
      <Dialog open={mergeDialog} onClose={() => setMergeDialog(false)}>
        <DialogTitle>Merge Data Sources</DialogTitle>
        <DialogContent>
          <Typography variant="body2" paragraph>
            Combine data from different sources for unified analysis.
          </Typography>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <FormControl>
              <Typography variant="body2">Include:</Typography>
              <Box>
                <label>
                  <input
                    type="checkbox"
                    checked={mergeOptions.includeClipboard}
                    onChange={(e) => setMergeOptions({
                      ...mergeOptions,
                      includeClipboard: e.target.checked
                    })}
                  />
                  Clipboard Data ({dbStats.clipboard || 0} items)
                </label>
              </Box>
              <Box>
                <label>
                  <input
                    type="checkbox"
                    checked={mergeOptions.includeBookmarks}
                    onChange={(e) => setMergeOptions({
                      ...mergeOptions,
                      includeBookmarks: e.target.checked
                    })}
                  />
                  Bookmarks ({dbStats.bookmarks || 0} items)
                </label>
              </Box>
              <Box>
                <label>
                  <input
                    type="checkbox"
                    checked={mergeOptions.includeHistory}
                    onChange={(e) => setMergeOptions({
                      ...mergeOptions,
                      includeHistory: e.target.checked
                    })}
                  />
                  Browser History ({dbStats.history || 0} items)
                </label>
              </Box>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMergeDialog(false)}>Cancel</Button>
          <Button onClick={handleMerge} variant="contained">
            Merge
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default DatabaseManager
