import React, { useState, useEffect, useCallback } from 'react'
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
  Checkbox,
  Alert,
  Snackbar,
  Toolbar,
  Tooltip,
  Menu,
  MenuItem as MenuItemComponent,
  ListItemIcon,
  ListItemText,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material'
import {
  Edit,
  Delete,
  Add,
  Search,
  FilterList,
  MoreVert,
  ContentCopy,
  Download,
  Upload,
  Refresh,
  Clear,
  ExpandMore,
  Visibility,
  Label,
  Category,
  DateRange,
  Storage
} from '@mui/icons-material'
// Temporarily use direct API calls instead of service
// import ClipboardCRUDService from '../services/ClipboardCRUDService'

function ClipboardCRUDManager() {
  // State management
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(25)
  const [totalCount, setTotalCount] = useState(0)
  const [selected, setSelected] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState({
    contentType: '',
    category: '',
    dateFrom: '',
    dateTo: ''
  })

  // Dialog states
  const [editDialog, setEditDialog] = useState(false)
  const [createDialog, setCreateDialog] = useState(false)
  const [deleteDialog, setDeleteDialog] = useState(false)
  const [viewDialog, setViewDialog] = useState(false)
  const [currentEntry, setCurrentEntry] = useState(null)

  // Form states
  const [formData, setFormData] = useState({
    content: '',
    content_type: 'Text',
    category: 'general',
    tags: []
  })

  // Menu states
  const [anchorEl, setAnchorEl] = useState(null)
  const [bulkMenuAnchor, setBulkMenuAnchor] = useState(null)

  // Load clipboard data using direct API call
  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.append('limit', rowsPerPage)
      params.append('offset', page * rowsPerPage)
      if (searchQuery) params.append('search', searchQuery)
      if (filters.contentType) params.append('content_type', filters.contentType)
      if (filters.category) params.append('category', filters.category)
      if (filters.dateFrom) params.append('date_from', filters.dateFrom)
      if (filters.dateTo) params.append('date_to', filters.dateTo)

      const response = await fetch(`http://localhost:3001/api/clipboard/history?${params.toString()}`)
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`)
      }

      const data = await response.json()
      setEntries(Array.isArray(data) ? data : data.entries || [])
      setTotalCount(Array.isArray(data) ? data.length : data.total || 0)
      setError(null)
    } catch (err) {
      setError('Failed to load clipboard data: ' + err.message)
      // Fallback to empty data
      setEntries([])
      setTotalCount(0)
    } finally {
      setLoading(false)
    }
  }, [page, rowsPerPage, searchQuery, filters])

  // Load data on component mount and when dependencies change
  useEffect(() => {
    loadData()
  }, [loadData])

  // Handle page change
  const handlePageChange = (event, newPage) => {
    setPage(newPage)
  }

  // Handle rows per page change
  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  // Handle selection
  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelected(entries.map(entry => entry.id))
    } else {
      setSelected([])
    }
  }

  const handleSelectOne = (id) => {
    const selectedIndex = selected.indexOf(id)
    let newSelected = []

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, id)
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1))
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1))
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1)
      )
    }

    setSelected(newSelected)
  }

  // CRUD Operations using direct API calls
  const handleCreate = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/clipboard/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: formData.content,
          content_type: formData.content_type,
          category: formData.category,
          tags: formData.tags,
          timestamp: new Date().toISOString(),
          source: 'manual'
        })
      })

      if (!response.ok) throw new Error(`Create failed: ${response.status}`)

      setSuccess('Entry created successfully')
      setCreateDialog(false)
      setFormData({ content: '', content_type: 'Text', category: 'general', tags: [] })
      loadData()
    } catch (err) {
      setError('Failed to create entry: ' + err.message)
    }
  }

  const handleUpdate = async () => {
    try {
      const response = await fetch(`http://localhost:3001/api/clipboard/entry/${currentEntry.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          updated_at: new Date().toISOString()
        })
      })

      if (!response.ok) throw new Error(`Update failed: ${response.status}`)

      setSuccess('Entry updated successfully')
      setEditDialog(false)
      setCurrentEntry(null)
      loadData()
    } catch (err) {
      setError('Failed to update entry: ' + err.message)
    }
  }

  const handleDelete = async (id = null) => {
    try {
      if (id) {
        const response = await fetch(`http://localhost:3001/api/clipboard/entry/${id}`, {
          method: 'DELETE'
        })
        if (!response.ok) throw new Error(`Delete failed: ${response.status}`)
        setSuccess('Entry deleted successfully')
      } else if (selected.length > 0) {
        // For now, delete one by one (bulk delete would need API support)
        for (const entryId of selected) {
          const response = await fetch(`http://localhost:3001/api/clipboard/entry/${entryId}`, {
            method: 'DELETE'
          })
          if (!response.ok) throw new Error(`Delete failed: ${response.status}`)
        }
        setSuccess(`${selected.length} entries deleted successfully`)
        setSelected([])
      }
      setDeleteDialog(false)
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
      content_type: entry.content_type,
      category: entry.category || 'general',
      tags: entry.tags || []
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

  const formatSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
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
      'Email': 'info',
      'Number': 'warning',
      'HTML': 'error'
    }
    return colors[type] || 'default'
  }

  // Search and filter handlers
  const handleSearch = () => {
    setPage(0)
    loadData()
  }

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }))
    setPage(0)
  }

  const clearFilters = () => {
    setFilters({
      contentType: '',
      category: '',
      dateFrom: '',
      dateTo: ''
    })
    setSearchQuery('')
    setPage(0)
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

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Typography variant="h4" gutterBottom>
        <Storage sx={{ mr: 1, verticalAlign: 'middle' }} />
        Clipboard Data Management
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Professional CRUD interface for managing your clipboard history data.
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

      {/* Search and Filters */}
      <Accordion sx={{ mb: 3 }}>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6">
            <FilterList sx={{ mr: 1, verticalAlign: 'middle' }} />
            Search & Filters
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search content"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  endAdornment: (
                    <IconButton onClick={handleSearch}>
                      <Search />
                    </IconButton>
                  )
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Content Type</InputLabel>
                <Select
                  value={filters.contentType}
                  onChange={(e) => handleFilterChange('contentType', e.target.value)}
                  label="Content Type"
                >
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="Text">Text</MenuItem>
                  <MenuItem value="URL">URL</MenuItem>
                  <MenuItem value="JSON">JSON</MenuItem>
                  <MenuItem value="CSV">CSV</MenuItem>
                  <MenuItem value="Email">Email</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  label="Category"
                >
                  <MenuItem value="">All Categories</MenuItem>
                  <MenuItem value="general">General</MenuItem>
                  <MenuItem value="web">Web</MenuItem>
                  <MenuItem value="data">Data</MenuItem>
                  <MenuItem value="communication">Communication</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                type="date"
                label="From Date"
                value={filters.dateFrom}
                onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                type="date"
                label="To Date"
                value={filters.dateTo}
                onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
            <Button variant="contained" onClick={handleSearch} startIcon={<Search />}>
              Search
            </Button>
            <Button variant="outlined" onClick={clearFilters} startIcon={<Clear />}>
              Clear Filters
            </Button>
            <Button variant="outlined" onClick={loadData} startIcon={<Refresh />}>
              Refresh
            </Button>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Toolbar */}
      <Toolbar sx={{ pl: 0, pr: 0 }}>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {selected.length > 0 ? `${selected.length} selected` : `${totalCount} entries`}
        </Typography>
        
        {selected.length > 0 && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              onClick={() => setDeleteDialog(true)}
            >
              Delete Selected
            </Button>
          </Box>
        )}
        
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialog(true)}
          sx={{ ml: 1 }}
        >
          Add Entry
        </Button>
      </Toolbar>

      {/* Loading indicator */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Data Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={selected.length > 0 && selected.length < entries.length}
                  checked={entries.length > 0 && selected.length === entries.length}
                  onChange={handleSelectAll}
                />
              </TableCell>
              <TableCell>Content</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {entries.map((entry) => (
              <TableRow
                key={entry.id}
                hover
                selected={selected.indexOf(entry.id) !== -1}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selected.indexOf(entry.id) !== -1}
                    onChange={() => handleSelectOne(entry.id)}
                  />
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                      {getContentPreview(entry.content)}
                    </Typography>
                    {entry.tags && entry.tags.length > 0 && (
                      <Box sx={{ mt: 0.5 }}>
                        {entry.tags.slice(0, 2).map((tag, index) => (
                          <Chip key={index} label={tag} size="small" sx={{ mr: 0.5 }} />
                        ))}
                        {entry.tags.length > 2 && (
                          <Chip label={`+${entry.tags.length - 2}`} size="small" />
                        )}
                      </Box>
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={entry.content_type}
                    color={getContentTypeColor(entry.content_type)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{entry.category || 'general'}</TableCell>
                <TableCell>{formatSize(entry.size_bytes || 0)}</TableCell>
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
                        onClick={() => {
                          setCurrentEntry(entry)
                          setDeleteDialog(true)
                        }}
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
        count={totalCount}
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
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={6}>
              <FormControl fullWidth>
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
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                  label="Category"
                >
                  <MenuItem value="general">General</MenuItem>
                  <MenuItem value="web">Web</MenuItem>
                  <MenuItem value="data">Data</MenuItem>
                  <MenuItem value="communication">Communication</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
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
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={6}>
              <FormControl fullWidth>
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
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                  label="Category"
                >
                  <MenuItem value="general">General</MenuItem>
                  <MenuItem value="web">Web</MenuItem>
                  <MenuItem value="data">Data</MenuItem>
                  <MenuItem value="communication">Communication</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
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
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Content Type:</Typography>
                      <Chip label={currentEntry.content_type} color={getContentTypeColor(currentEntry.content_type)} />
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Category:</Typography>
                      <Typography variant="body2">{currentEntry.category || 'general'}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Size:</Typography>
                      <Typography variant="body2">{formatSize(currentEntry.size_bytes || 0)}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Date:</Typography>
                      <Typography variant="body2">{formatDate(currentEntry.timestamp)}</Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
              
              <Typography variant="subtitle2" gutterBottom>Content:</Typography>
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

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <Typography>
            {currentEntry 
              ? 'Are you sure you want to delete this entry?'
              : `Are you sure you want to delete ${selected.length} selected entries?`
            }
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
          <Button 
            onClick={() => handleDelete(currentEntry?.id)}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ClipboardCRUDManager
