import React, { useState, useEffect, useMemo } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Grid,
  Card,
  CardContent,
  Button,
  ButtonGroup,
  Slider,
  Switch,
  FormControlLabel,
  Autocomplete,
  Pagination,
  LinearProgress,
  Alert
} from '@mui/material'
import {
  Search,
  FilterList,
  ViewList,
  ViewModule,
  Timeline,
  BarChart,
  PieChart,
  ScatterPlot,
  TableChart,
  CloudQueue
} from '@mui/icons-material'

function ImprovedClipboardVisualizations({ clipboardData = [] }) {
  // State management for filtering and visualization
  const [searchQuery, setSearchQuery] = useState('')
  const [contentTypeFilter, setContentTypeFilter] = useState('all')
  const [dateRange, setDateRange] = useState([0, 100])
  const [sizeFilter, setSizeFilter] = useState([0, 100])
  const [visualizationType, setVisualizationType] = useState('timeline')
  const [itemsPerPage, setItemsPerPage] = useState(50)
  const [currentPage, setCurrentPage] = useState(1)
  const [showFilters, setShowFilters] = useState(true)

  // Process and filter data
  const processedData = useMemo(() => {
    if (!Array.isArray(clipboardData) || clipboardData.length === 0) {
      return []
    }

    // Add computed fields
    const enrichedData = clipboardData.map((item, index) => ({
      ...item,
      id: item.id || index,
      size_bytes: item.size_bytes || new Blob([item.content || '']).size,
      timestamp: new Date(item.timestamp || Date.now()),
      content_preview: (item.content || '').substring(0, 100),
      word_count: (item.content || '').split(/\s+/).length,
      has_url: /https?:\/\//.test(item.content || ''),
      has_email: /@.*\./.test(item.content || ''),
      content_length: (item.content || '').length
    }))

    // Apply filters
    let filtered = enrichedData

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(item =>
        (item.content || '').toLowerCase().includes(query) ||
        (item.content_type || '').toLowerCase().includes(query)
      )
    }

    // Content type filter
    if (contentTypeFilter !== 'all') {
      filtered = filtered.filter(item => {
        const type = (item.content_type || 'text').toLowerCase()
        if (contentTypeFilter === 'url') return item.has_url
        if (contentTypeFilter === 'email') return item.has_email
        return type.includes(contentTypeFilter)
      })
    }

    // Date range filter
    if (filtered.length > 0) {
      const sortedByDate = [...filtered].sort((a, b) => a.timestamp - b.timestamp)
      const startIndex = Math.floor((dateRange[0] / 100) * sortedByDate.length)
      const endIndex = Math.ceil((dateRange[1] / 100) * sortedByDate.length)
      filtered = sortedByDate.slice(startIndex, endIndex)
    }

    // Size filter
    if (filtered.length > 0) {
      const maxSize = Math.max(...filtered.map(item => item.size_bytes))
      const minSize = (sizeFilter[0] / 100) * maxSize
      const maxSizeFilter = (sizeFilter[1] / 100) * maxSize
      filtered = filtered.filter(item => 
        item.size_bytes >= minSize && item.size_bytes <= maxSizeFilter
      )
    }

    return filtered
  }, [clipboardData, searchQuery, contentTypeFilter, dateRange, sizeFilter])

  // Pagination
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return processedData.slice(startIndex, startIndex + itemsPerPage)
  }, [processedData, currentPage, itemsPerPage])

  // Statistics
  const stats = useMemo(() => {
    if (processedData.length === 0) return {}

    const totalSize = processedData.reduce((sum, item) => sum + item.size_bytes, 0)
    const avgSize = totalSize / processedData.length
    const contentTypes = [...new Set(processedData.map(item => item.content_type || 'text'))]
    const urlCount = processedData.filter(item => item.has_url).length
    const emailCount = processedData.filter(item => item.has_email).length

    return {
      totalEntries: processedData.length,
      totalSize,
      avgSize,
      contentTypes,
      urlCount,
      emailCount,
      dateRange: {
        earliest: Math.min(...processedData.map(item => item.timestamp)),
        latest: Math.max(...processedData.map(item => item.timestamp))
      }
    }
  }, [processedData])

  // Get unique content types for filter
  const availableContentTypes = useMemo(() => {
    const types = new Set()
    clipboardData.forEach(item => {
      types.add(item.content_type || 'text')
      if (item.has_url) types.add('url')
      if (item.has_email) types.add('email')
    })
    return Array.from(types)
  }, [clipboardData])

  // Timeline Visualization Component
  const TimelineVisualization = () => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          📈 Timeline View ({processedData.length} entries)
        </Typography>
        <Box sx={{ height: 300, display: 'flex', flexDirection: 'column', gap: 1 }}>
          {paginatedData.map((item, index) => (
            <Box
              key={item.id}
              sx={{
                display: 'flex',
                alignItems: 'center',
                p: 1,
                border: 1,
                borderColor: 'grey.300',
                borderRadius: 1,
                bgcolor: 'grey.50'
              }}
            >
              <Typography variant="caption" sx={{ minWidth: 120, mr: 2 }}>
                {item.timestamp.toLocaleString()}
              </Typography>
              <Chip
                label={item.content_type || 'text'}
                size="small"
                color="primary"
                sx={{ mr: 1 }}
              />
              <Typography variant="body2" sx={{ flexGrow: 1 }}>
                {item.content_preview}...
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {(item.size_bytes / 1024).toFixed(1)}KB
              </Typography>
            </Box>
          ))}
        </Box>
        <Pagination
          count={Math.ceil(processedData.length / itemsPerPage)}
          page={currentPage}
          onChange={(e, page) => setCurrentPage(page)}
          sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}
        />
      </CardContent>
    </Card>
  )

  // Data Table Visualization
  const DataTableVisualization = () => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          📊 Data Table ({processedData.length} entries)
        </Typography>
        <Box sx={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5' }}>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Date</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Type</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Content</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Size</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Words</th>
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((item) => (
                <tr key={item.id}>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                    {item.timestamp.toLocaleDateString()}
                  </td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                    <Chip label={item.content_type || 'text'} size="small" />
                  </td>
                  <td style={{ padding: '8px', border: '1px solid #ddd', maxWidth: '300px' }}>
                    {item.content_preview}...
                  </td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                    {(item.size_bytes / 1024).toFixed(1)}KB
                  </td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                    {item.word_count}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Box>
        <Pagination
          count={Math.ceil(processedData.length / itemsPerPage)}
          page={currentPage}
          onChange={(e, page) => setCurrentPage(page)}
          sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}
        />
      </CardContent>
    </Card>
  )

  // Statistics Cards
  const StatisticsCards = () => (
    <Grid container spacing={2} sx={{ mb: 2 }}>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" color="primary">
              {stats.totalEntries || 0}
            </Typography>
            <Typography variant="body2">Total Entries</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" color="secondary">
              {((stats.totalSize || 0) / 1024 / 1024).toFixed(1)}MB
            </Typography>
            <Typography variant="body2">Total Size</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" color="success.main">
              {stats.urlCount || 0}
            </Typography>
            <Typography variant="body2">URLs Found</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" color="warning.main">
              {stats.emailCount || 0}
            </Typography>
            <Typography variant="body2">Emails Found</Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  // Content Type Distribution
  const ContentTypeDistribution = () => {
    const typeStats = useMemo(() => {
      const counts = {}
      processedData.forEach(item => {
        const type = item.content_type || 'text'
        counts[type] = (counts[type] || 0) + 1
      })
      return Object.entries(counts).map(([type, count]) => ({
        type,
        count,
        percentage: ((count / processedData.length) * 100).toFixed(1)
      }))
    }, [processedData])

    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📊 Content Type Distribution
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {typeStats.map(({ type, count, percentage }) => (
              <Chip
                key={type}
                label={`${type}: ${count} (${percentage}%)`}
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>
        </CardContent>
      </Card>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        🔍 Improved Clipboard Visualizations
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Interactive filtering and better UX for large clipboard datasets
      </Typography>

      {/* Filter Controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            🔧 Filters & Controls
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={showFilters}
                onChange={(e) => setShowFilters(e.target.checked)}
              />
            }
            label="Show Filters"
          />
        </Box>

        {showFilters && (
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search Content"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Content Type</InputLabel>
                <Select
                  value={contentTypeFilter}
                  onChange={(e) => setContentTypeFilter(e.target.value)}
                  label="Content Type"
                >
                  <MenuItem value="all">All Types</MenuItem>
                  {availableContentTypes.map(type => (
                    <MenuItem key={type} value={type}>{type}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Visualization</InputLabel>
                <Select
                  value={visualizationType}
                  onChange={(e) => setVisualizationType(e.target.value)}
                  label="Visualization"
                >
                  <MenuItem value="timeline">📈 Timeline View</MenuItem>
                  <MenuItem value="table">📊 Data Table</MenuItem>
                  <MenuItem value="stats">📈 Statistics</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Date Range</Typography>
              <Slider
                value={dateRange}
                onChange={(e, newValue) => setDateRange(newValue)}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${value}%`}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Size Range</Typography>
              <Slider
                value={sizeFilter}
                onChange={(e, newValue) => setSizeFilter(newValue)}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${value}%`}
              />
            </Grid>
          </Grid>
        )}
      </Paper>

      {/* Statistics Overview */}
      <StatisticsCards />

      {/* Content Type Distribution */}
      <ContentTypeDistribution />

      {/* Main Visualization */}
      {visualizationType === 'timeline' && <TimelineVisualization />}
      {visualizationType === 'table' && <DataTableVisualization />}
      {visualizationType === 'stats' && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📊 Detailed Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Data Overview:</Typography>
                <Typography>• Total Entries: {stats.totalEntries}</Typography>
                <Typography>• Total Size: {((stats.totalSize || 0) / 1024 / 1024).toFixed(2)}MB</Typography>
                <Typography>• Average Size: {((stats.avgSize || 0) / 1024).toFixed(1)}KB</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Content Analysis:</Typography>
                <Typography>• URLs Found: {stats.urlCount}</Typography>
                <Typography>• Emails Found: {stats.emailCount}</Typography>
                <Typography>• Content Types: {(stats.contentTypes || []).length}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Performance Info */}
      {processedData.length > 100 && (
        <Alert severity="info" sx={{ mt: 2 }}>
          💡 Large dataset detected ({processedData.length} entries). 
          Use filters to narrow down results for better performance.
        </Alert>
      )}
    </Box>
  )
}

export default ImprovedClipboardVisualizations

// Additional component for Crossfilter-based interactive dashboard
// This will be implemented in a separate file for better performance
