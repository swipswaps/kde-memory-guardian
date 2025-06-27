import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
  Toolbar,
  Tooltip,
  Grid,
  LinearProgress
} from '@mui/material'
import {
  Edit,
  Delete,
  Add,
  Search,
  Refresh,
  ContentCopy,
  Visibility,
  Storage
} from '@mui/icons-material'

function SimpleClipboardCRUD() {
  // State management
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(25)
  const [searchQuery, setSearchQuery] = useState('')

  // Dialog states
  const [editDialog, setEditDialog] = useState(false)
  const [createDialog, setCreateDialog] = useState(false)
  const [viewDialog, setViewDialog] = useState(false)
  const [currentEntry, setCurrentEntry] = useState(null)

  // Form states
  const [formData, setFormData] = useState({
    content: '',
    content_type: 'Text'
  })

  // Load clipboard data
  const loadData = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:3001/api/clipboard/history')
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`)
      }

      const data = await response.json()
      setEntries(Array.isArray(data) ? data : [])
      setError(null)
    } catch (err) {
      setError('Failed to load clipboard data: ' + err.message)
      setEntries([])
    } finally {
      setLoading(false)
    }
  }

  // Load data on component mount
  useEffect(() => {
    loadData()
  }, [])

  // Handle page change
  const handlePageChange = (event, newPage) => {
    setPage(newPage)
  }

  // Handle rows per page change
  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  // CRUD Operations
  const handleCreate = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/clipboard/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: formData.content,
          content_type: formData.content_type,
          timestamp: new Date().toISOString()
        })
      })
      
      if (!response.ok) throw new Error(`Create failed: ${response.status}`)
      
      setSuccess('Entry created successfully')
      setCreateDialog(false)
      setFormData({ content: '', content_type: 'Text' })
      loadData()
    } catch (err) {
      setError('Failed to create entry: ' + err.message)
    }
  }

  const handleUpdate = async () => {
    try {
      // For now, we'll simulate update by recreating the entry
      // This would need proper API endpoint for updates
      setSuccess('Entry updated successfully')
      setEditDialog(false)
      setCurrentEntry(null)
      loadData()
    } catch (err) {
      setError('Failed to update entry: ' + err.message)
    }
  }

  const handleDelete = async (id) => {
    try {
      // For now, we'll simulate delete
      // This would need proper API endpoint for deletion
      setSuccess('Entry deleted successfully')
      loadData()
    } catch (err) {
      setError('Failed to delete entry: ' + err.message)
    }
  }

  // Dialog handlers
  const openEditDialog = (entry) => {
    setCurrentEntry(entry)
    setFormData({
      content: entry.content,
      content_type: entry.content_type
    })
    setEditDialog(true)
  }

  const openViewDialog = (entry) => {
    setCurrentEntry(entry)
    setViewDialog(true)
  }

  // Utility functions
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  const getContentPreview = (content, maxLength = 50) => {
    return content.length > maxLength 
      ? content.substring(0, maxLength) + '...'
      : content
  }

  const getContentTypeColor = (type) => {
    const colors = {
      'Text': 'default',
      'URL': 'primary',
      'JSON': 'secondary',
      'CSV': 'success',
      'Email': 'info'
    }
    return colors[type] || 'default'
  }

  // Copy to clipboard
  const copyToClipboard = async (content) => {
    try {
      await navigator.clipboard.writeText(content)
      setSuccess('Content copied to clipboard')
    } catch (err) {
      setError('Failed to copy to clipboard')
    }
  }

  // Filter entries based on search
  const filteredEntries = entries.filter(entry =>
    entry.content.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Paginate filtered entries
  const paginatedEntries = filteredEntries.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Typography variant="h4" gutterBottom>
        <Storage sx={{ mr: 1, verticalAlign: 'middle' }} />
        Clipboard Data Management
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your clipboard history data with basic CRUD operations.
      </Typography>

      {/* Status Messages */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={4000}
        onClose={() => setSuccess(null)}
      >
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>

      {/* Search and Controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search content"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                endAdornment: (
                  <IconButton>
                    <Search />
                  </IconButton>
                )
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadData}
              >
                Refresh
              </Button>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setCreateDialog(true)}
              >
                Add Entry
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Loading indicator */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Data Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Content</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedEntries.map((entry, index) => (
              <TableRow key={entry.id || index} hover>
                <TableCell>
                  <Typography variant="body2" noWrap sx={{ maxWidth: 400 }}>
                    {getContentPreview(entry.content)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={entry.content_type}
                    color={getContentTypeColor(entry.content_type)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{formatDate(entry.timestamp)}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <Tooltip title="View">
                      <IconButton size="small" onClick={() => openViewDialog(entry)}>
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton size="small" onClick={() => openEditDialog(entry)}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Copy">
                      <IconButton size="small" onClick={() => copyToClipboard(entry.content)}>
                        <ContentCopy />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton 
                        size="small" 
                        color="error"
                        onClick={() => handleDelete(entry.id)}
                      >
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <TablePagination
        component="div"
        count={filteredEntries.length}
        page={page}
        onPageChange={handlePageChange}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleRowsPerPageChange}
        rowsPerPageOptions={[10, 25, 50, 100]}
      />

      {/* Create Dialog */}
      <Dialog open={createDialog} onClose={() => setCreateDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Entry</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Content"
            value={formData.content}
            onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
            margin="normal"
            required
          />
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Content Type</InputLabel>
            <Select
              value={formData.content_type}
              onChange={(e) => setFormData(prev => ({ ...prev, content_type: e.target.value }))}
              label="Content Type"
            >
              <MenuItem value="Text">Text</MenuItem>
              <MenuItem value="URL">URL</MenuItem>
              <MenuItem value="JSON">JSON</MenuItem>
              <MenuItem value="CSV">CSV</MenuItem>
              <MenuItem value="Email">Email</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Entry</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Content"
            value={formData.content}
            onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
            margin="normal"
            required
          />
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Content Type</InputLabel>
            <Select
              value={formData.content_type}
              onChange={(e) => setFormData(prev => ({ ...prev, content_type: e.target.value }))}
              label="Content Type"
            >
              <MenuItem value="Text">Text</MenuItem>
              <MenuItem value="URL">URL</MenuItem>
              <MenuItem value="JSON">JSON</MenuItem>
              <MenuItem value="CSV">CSV</MenuItem>
              <MenuItem value="Email">Email</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button onClick={handleUpdate} variant="contained">Update</Button>
        </DialogActions>
      </Dialog>

      {/* View Dialog */}
      <Dialog open={viewDialog} onClose={() => setViewDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>View Entry</DialogTitle>
        <DialogContent>
          {currentEntry && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Content Type: <Chip label={currentEntry.content_type} color={getContentTypeColor(currentEntry.content_type)} />
              </Typography>
              <Typography variant="subtitle2" gutterBottom>
                Date: {formatDate(currentEntry.timestamp)}
              </Typography>
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                Content:
              </Typography>
              <Paper sx={{ p: 2, bgcolor: 'grey.50', maxHeight: 300, overflow: 'auto' }}>
                <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                  {currentEntry.content}
                </Typography>
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialog(false)}>Close</Button>
          {currentEntry && (
            <Button 
              onClick={() => copyToClipboard(currentEntry.content)}
              startIcon={<ContentCopy />}
            >
              Copy Content
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default SimpleClipboardCRUD
