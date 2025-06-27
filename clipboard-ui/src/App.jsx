import React, { useState, useEffect } from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Box,
  Paper,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Alert,
  Snackbar,
  CircularProgress,
  Backdrop,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Collapse,
  IconButton,
  Tabs,
  Tab,
} from '@mui/material'
import {
  BarChart,
  PieChart,
  ScatterPlot,
  BubbleChart,
  DonutLarge,
  TrendingUp,
  Refresh,
  DataUsage,
  AccountTree,
  Search,
  FilterList,
  Clear,
  ExpandMore,
  ExpandLess,
  Visibility,
  Download,
  Share,
  Timeline,
  AutoGraph,
  Memory,
  Dashboard,
  Hub,
  Storage,
  Settings,
  AutoAwesome,
} from '@mui/icons-material'
import ClipboardDataService from './services/ClipboardDataService'
// Removed ClipboardCRUDService to fix import issues
import SimpleChartRenderer from './components/SimpleChartRenderer'
import DataPreview from './components/DataPreview'
import ChartSelector from './components/ChartSelector'
import SmartSuggestions from './components/SmartSuggestions'
import SimpleTest from './components/SimpleTest'
import SmartInsights from './components/SmartInsights'
import ImprovedMemoryDashboard from './components/ImprovedMemoryDashboard'
import Neo4jVisualizer from './components/Neo4jVisualizer'
import DatabaseManager from './components/DatabaseManager'
import SimpleClipboardCRUD from './components/SimpleClipboardCRUD'
import ImprovedClipboardVisualizations from './components/ImprovedClipboardVisualizations'
import InteractiveClipboardDashboard from './components/InteractiveClipboardDashboard'
import EnhancedClipboardDashboard from './components/EnhancedClipboardDashboard'

// Focused on the most useful chart types based on research
const CHART_TYPES = [
  { id: 'table', name: 'Data Table', icon: <DataUsage />, color: '#2e7d32', description: 'Explore raw data in spreadsheet format' },
  { id: 'bar', name: 'Bar Chart', icon: <BarChart />, color: '#1976d2', description: 'Compare categories and values' },
  { id: 'line', name: 'Line Chart', icon: <TrendingUp />, color: '#388e3c', description: 'Show trends over time' },
  { id: 'pie', name: 'Pie Chart', icon: <PieChart />, color: '#dc004e', description: 'Parts of a whole (3-8 categories)' },
  { id: 'wordcloud', name: 'Word Cloud', icon: <DataUsage />, color: '#9c27b0', description: 'Text frequency visualization' },
  { id: 'gantt', name: 'Timeline', icon: <Timeline />, color: '#f57c00', description: 'Project schedules and timelines' },
  { id: 'network', name: 'Network Graph', icon: <Hub />, color: '#00695c', description: 'Neo4j-style relationship visualization' },
]

function App() {
  const [clipboardData, setClipboardData] = useState([])
  const [filteredData, setFilteredData] = useState([])
  const [selectedChart, setSelectedChart] = useState('network')
  const [processedData, setProcessedData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [dataStats, setDataStats] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [contentTypeFilter, setContentTypeFilter] = useState('all')
  const [showDataPreview, setShowDataPreview] = useState(false)
  const [currentTab, setCurrentTab] = useState(0)

  // Load clipboard data on component mount and force refresh
  useEffect(() => {
    console.log('App mounted - loading real clipboard data immediately...')
    loadClipboardData()

    // Also set up periodic refresh to ensure data stays current
    const interval = setInterval(() => {
      console.log('Periodic refresh of clipboard data...')
      loadClipboardData()
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [])

  // Filter data when search term or filter changes
  useEffect(() => {
    let filtered = clipboardData

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.content_type.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Apply content type filter
    if (contentTypeFilter !== 'all') {
      filtered = filtered.filter(item => {
        const type = getContentTypeLabel(item.content)
        return type.toLowerCase() === contentTypeFilter.toLowerCase()
      })
    }

    setFilteredData(filtered)
  }, [clipboardData, searchTerm, contentTypeFilter])

  // Process data when filtered data or chart type changes
  useEffect(() => {
    if (filteredData.length > 0) {
      processDataForChart(filteredData, selectedChart)
    }
  }, [filteredData, selectedChart])

  const loadClipboardData = async () => {
    console.log('Loading real clipboard data for graphs...')
    setLoading(true)
    try {
      // Use direct API call to get actual clipboard data (all entries)
      console.log('Fetching real clipboard data from API...')
      const response = await fetch('http://localhost:3001/api/clipboard/history?limit=1000')

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`)
      }

      const data = await response.json()
      console.log('Received real data:', data.length, 'entries')

      if (!Array.isArray(data)) {
        throw new Error('API returned invalid data format')
      }

      setClipboardData(data)

      // Calculate real statistics from actual clipboard data
      const stats = {
        totalEntries: data.length,
        textEntries: data.filter(item => item.content_type === 'Text' || item.content_type === 'text').length,
        jsonEntries: data.filter(item =>
          item.content_type === 'JSON' ||
          item.content_type === 'json' ||
          (item.content && (item.content.trim().startsWith('{') || item.content.trim().startsWith('[')))
        ).length,
        csvEntries: data.filter(item =>
          item.content_type === 'CSV' ||
          item.content_type === 'csv' ||
          (item.content && item.content.includes(',') && item.content.includes('\n'))
        ).length,
        urlEntries: data.filter(item =>
          item.content_type === 'URL' ||
          item.content_type === 'url' ||
          (item.content && (item.content.includes('http://') || item.content.includes('https://')))
        ).length,
        emailEntries: data.filter(item =>
          item.content_type === 'Email' ||
          item.content_type === 'email' ||
          (item.content && item.content.includes('@') && item.content.includes('.'))
        ).length,
        totalSize: data.reduce((sum, item) => sum + (item.size_bytes || new Blob([item.content || '']).size), 0),
        recentEntries: data.filter(item => {
          const entryDate = new Date(item.timestamp)
          const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
          return entryDate > oneDayAgo
        }).length,
        // Extract actual domains from URLs for better categorization
        domains: [...new Set(data
          .filter(item => item.content && (item.content.includes('http://') || item.content.includes('https://')))
          .map(item => {
            try {
              const url = new URL(item.content.match(/(https?:\/\/[^\s]+)/)[0])
              return url.hostname
            } catch {
              return null
            }
          })
          .filter(Boolean)
        )]
      }

      console.log('Calculated real statistics:', stats)
      setDataStats(stats)

      setSnackbarOpen(true)
    } catch (err) {
      console.error('Failed to load clipboard data:', err)
      setError('Failed to load clipboard data: ' + err.message)
      // Set empty data instead of keeping old data
      setClipboardData([])
      setDataStats({
        totalEntries: 0,
        textEntries: 0,
        jsonEntries: 0,
        csvEntries: 0,
        urlEntries: 0,
        emailEntries: 0,
        totalSize: 0,
        recentEntries: 0,
        domains: []
      })
    } finally {
      setLoading(false)
    }
  }

  const processDataForChart = async (data, chartType) => {
    setLoading(true)
    try {
      console.log('Processing data for chart:', chartType, 'with data length:', data?.length)

      // Process data directly for D3.js charts
      const processed = processDataForVisualization(data, chartType)
      console.log('Processed data result:', processed)
      setProcessedData(processed)
    } catch (err) {
      console.error('Chart processing error:', err)
      setError('Failed to process data for visualization: ' + err.message)
    } finally {
      setLoading(false)
    }
  }



  // Direct data processing function (inspired by Graphify approach)
  const processDataForVisualization = (data, chartType) => {
    console.log('processDataForVisualization called with:', { chartType, dataLength: data?.length })

    if (!data || data.length === 0) {
      console.log('No data available for processing')
      return null
    }

    let result
    switch (chartType) {
      case 'bar':
        result = processForBarChart(data)
        break
      case 'pie':
        result = processForPieChart(data)
        break
      case 'line':
        result = processForLineChart(data)
        break
      case 'wordcloud':
        result = processForWordCloud(data)
        break
      case 'gantt':
      case 'timeline':
        result = processForTimeline(data)
        break
      case 'network':
        result = processForNetworkGraph(data)
        break
      default:
        result = data
    }

    console.log('processDataForVisualization result:', result)
    return result
  }

  const processForBarChart = (data) => {
    console.log('processForBarChart called with data:', data)

    // Find CSV data and convert to chart format
    const csvData = data.find(item =>
      item.content && item.content.includes(',') && item.content.includes('\n')
    )

    if (csvData) {
      console.log('Found CSV data:', csvData.content.substring(0, 100))
      const lines = csvData.content.trim().split('\n')
      const headers = lines[0].split(',')
      const rows = lines.slice(1).map(line => line.split(','))

      // Create bar chart data
      const result = rows.map(row => ({
        label: row[0],  // ChartRenderer expects 'label' not 'name'
        value: parseInt(row[1]) || 0
      }))
      console.log('CSV chart data:', result)
      return result
    }

    // Fallback: content type distribution
    console.log('Using content type distribution fallback')
    const contentTypes = {}
    data.forEach(item => {
      const type = item.content_type || 'Unknown'
      contentTypes[type] = (contentTypes[type] || 0) + 1
    })

    const result = Object.entries(contentTypes).map(([name, value]) => ({
      label: name,  // ChartRenderer expects 'label' not 'name'
      value
    }))

    console.log('Content type distribution result:', result)
    return result
  }

  const processForPieChart = (data) => {
    // Similar to bar chart but formatted for pie
    return processForBarChart(data)
  }

  const processForLineChart = (data) => {
    // Create timeline of clipboard activity
    const dailyActivity = {}
    data.forEach(item => {
      const date = new Date(item.timestamp).toDateString()
      dailyActivity[date] = (dailyActivity[date] || 0) + 1
    })

    return Object.entries(dailyActivity).map(([date, count], index) => ({
      x: index,  // Line chart expects x,y coordinates
      y: count,
      label: date
    }))
  }

  const processForWordCloud = (data) => {
    // Combine all text content and create word frequency
    const allText = data
      .filter(item => item.content_type === 'Text')
      .map(item => item.content)
      .join(' ')

    const words = allText
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 3)

    const wordCount = {}
    words.forEach(word => {
      wordCount[word] = (wordCount[word] || 0) + 1
    })

    return Object.entries(wordCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 50)
      .map(([text, size]) => ({ text, size }))
  }

  const processForTimeline = (data) => {
    // Look for JSON data with timeline information
    const jsonData = data.find(item =>
      item.content.trim().startsWith('{') &&
      (item.content.includes('start') || item.content.includes('date'))
    )

    if (jsonData) {
      try {
        const parsed = JSON.parse(jsonData.content)
        if (parsed.projects) {
          return parsed.projects
        }
        if (parsed.tasks) {
          return parsed.tasks
        }
      } catch (e) {
        console.warn('Failed to parse JSON for timeline:', e)
      }
    }

    // Fallback: clipboard timeline
    return data.slice(0, 10).map(item => ({
      name: item.content.substring(0, 30) + '...',
      start: item.timestamp,
      end: item.timestamp
    }))
  }

  const processForNetworkGraph = (data) => {
    // Return raw data for Neo4jVisualizer to process
    // The Neo4jVisualizer component handles the complex graph processing
    return data
  }

  const handleChartChange = (chartType) => {
    setSelectedChart(chartType)
  }

  const handleRefresh = async () => {
    console.log('Manual refresh clicked')
    loadClipboardData()
  }

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue)
  }

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value)
  }

  const handleFilterChange = (event) => {
    setContentTypeFilter(event.target.value)
  }

  const clearFilters = () => {
    setSearchTerm('')
    setContentTypeFilter('all')
  }

  // Helper function to get content type
  const getContentTypeLabel = (content) => {
    if (content.trim().startsWith('{') || content.trim().startsWith('[')) {
      return 'JSON'
    }
    if (content.includes('http')) {
      return 'URL'
    }
    if (content.includes(',') && content.includes('\n')) {
      return 'CSV'
    }
    return 'Text'
  }

  const speedDialActions = [
    { icon: <Refresh />, name: 'Refresh Data', onClick: handleRefresh },
    { icon: <Visibility />, name: 'Toggle Preview', onClick: () => setShowDataPreview(!showDataPreview) },
    { icon: <Clear />, name: 'Clear Filters', onClick: clearFilters },
  ]

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* App Bar */}
      <AppBar position="static" elevation={0} sx={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(10px)' }}>
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}>
            <Typography variant="h6" component="div" sx={{ fontWeight: 700, color: 'white' }}>
              📋 Clipboard Intelligence
            </Typography>
            <Chip
              label="AI-Powered"
              size="small"
              sx={{
                backgroundColor: 'rgba(255,255,255,0.2)',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '0.7rem'
              }}
            />
          </Box>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Chip
              label={`${filteredData.length}/${clipboardData.length} entries`}
              color="secondary"
              variant="outlined"
              sx={{ color: 'white', borderColor: 'white' }}
            />
            {(searchTerm || contentTypeFilter !== 'all') && (
              <Chip
                label="Filtered"
                color="warning"
                size="small"
                sx={{ color: 'white' }}
              />
            )}
          </Box>
        </Toolbar>

        {/* Navigation Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'rgba(255,255,255,0.2)' }}>
          <Tabs
            value={currentTab}
            onChange={handleTabChange}
            sx={{
              '& .MuiTab-root': {
                color: 'rgba(255,255,255,0.7)',
                '&.Mui-selected': { color: 'white' }
              },
              '& .MuiTabs-indicator': { backgroundColor: 'white' }
            }}
          >
            <Tab icon={<Dashboard />} label="Clipboard Analytics" />
            <Tab icon={<TrendingUp />} label="Interactive Dashboard" />
            <Tab icon={<AutoAwesome />} label="Enhanced Dashboard" />
            <Tab icon={<Memory />} label="Memory Protection" />
            <Tab icon={<Storage />} label="Database Management" />
            <Tab icon={<Settings />} label="Clipboard CRUD" />
          </Tabs>
        </Box>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, pb: 10 }}>
        {/* Tab Content */}
        {currentTab === 0 && (
          <Grid container spacing={3}>
          {/* Dashboard Overview */}
          <Grid item xs={12}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                borderRadius: 3,
                background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.2)'
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  📊 Intelligence Dashboard
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Chip
                    icon={<Timeline />}
                    label="Live"
                    color="success"
                    variant="outlined"
                    sx={{ fontWeight: 'bold' }}
                  />
                  <Chip
                    icon={<AutoGraph />}
                    label="Smart Analysis"
                    color="info"
                    variant="outlined"
                    sx={{ fontWeight: 'bold' }}
                  />
                </Box>
              </Box>

              {/* Stats Grid */}
              {dataStats && (
                <Grid container spacing={3} sx={{ mb: 3 }}>
                  <Grid item xs={6} sm={3} lg={2}>
                    <Paper elevation={2} sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                      <Typography variant="h4" color="primary.main" fontWeight="bold">
                        {dataStats.totalEntries}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Entries
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3} lg={2}>
                    <Paper elevation={2} sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                      <Typography variant="h4" color="secondary.main" fontWeight="bold">
                        {dataStats.textEntries}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Text Items
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3} lg={2}>
                    <Paper elevation={2} sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                      <Typography variant="h4" color="success.main" fontWeight="bold">
                        {dataStats.jsonEntries}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        JSON Data
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3} lg={2}>
                    <Paper elevation={2} sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                      <Typography variant="h4" color="warning.main" fontWeight="bold">
                        {dataStats.csvEntries}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        CSV Files
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3} lg={2}>
                    <Paper elevation={2} sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                      <Typography variant="h4" color="info.main" fontWeight="bold">
                        {dataStats.urlEntries}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        URLs
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3} lg={2}>
                    <Paper elevation={2} sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                      <Typography variant="h4" color="error.main" fontWeight="bold">
                        {Math.round((filteredData.length / dataStats.totalEntries) * 100)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Filtered
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              )}

              {/* Quick Actions */}
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  startIcon={<Refresh />}
                  onClick={handleRefresh}
                  sx={{ borderRadius: 2 }}
                >
                  Refresh Data
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Clear />}
                  onClick={clearFilters}
                  disabled={!searchTerm && contentTypeFilter === 'all'}
                  sx={{ borderRadius: 2 }}
                >
                  Clear Filters
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Download />}
                  onClick={() => {
                    const csvContent = filteredData.map(item =>
                      `"${item.timestamp}","${item.content_type}","${item.content.replace(/"/g, '""')}"`
                    ).join('\n')
                    const blob = new Blob([`Timestamp,Type,Content\n${csvContent}`], { type: 'text/csv' })
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = 'clipboard_data.csv'
                    a.click()
                    URL.revokeObjectURL(url)
                  }}
                  sx={{ borderRadius: 2 }}
                >
                  Export CSV
                </Button>
              </Box>
            </Paper>
          </Grid>

          {/* Simple API Test - Collapsible */}
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ pb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6">
                    🧪 API Connection Test
                  </Typography>
                  <IconButton
                    onClick={() => setShowDataPreview(!showDataPreview)}
                    size="small"
                  >
                    {showDataPreview ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Box>
                <Collapse in={showDataPreview}>
                  <Box sx={{ mt: 2 }}>
                    <SimpleTest />
                  </Box>
                </Collapse>
              </CardContent>
            </Card>
          </Grid>

          {/* Debug Info */}
          <Grid item xs={12}>
            <Alert severity="info">
              <Typography variant="body2">
                <strong>Debug Info:</strong><br/>
                • clipboardData.length = {clipboardData.length}<br/>
                • filteredData.length = {filteredData.length}<br/>
                • loading = {loading.toString()}<br/>
                • error = {error || 'none'}<br/>
                • API URL = http://localhost:3001/api/clipboard/history<br/>
                • Last update = {new Date().toLocaleTimeString()}
              </Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={handleRefresh}
                sx={{ mt: 1 }}
              >
                Force Refresh Now
              </Button>
            </Alert>
          </Grid>

          {/* Smart Insights */}
          <Grid item xs={12}>
            <SmartInsights data={filteredData} />
          </Grid>

          {/* Smart Suggestions */}
          <Grid item xs={12}>
            <SmartSuggestions
              data={filteredData}
              onChartSelect={handleChartChange}
              selectedChart={selectedChart}
            />
          </Grid>

          {/* Search and Filter Controls */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  🔍 Search & Filter
                  {(searchTerm || contentTypeFilter !== 'all') && (
                    <Button
                      size="small"
                      onClick={clearFilters}
                      startIcon={<Clear />}
                      color="secondary"
                    >
                      Clear Filters
                    </Button>
                  )}
                </Typography>

                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Search clipboard content"
                      value={searchTerm}
                      onChange={handleSearchChange}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Search />
                          </InputAdornment>
                        ),
                      }}
                      placeholder="Search for text, URLs, keywords..."
                    />
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth>
                      <InputLabel>Content Type</InputLabel>
                      <Select
                        value={contentTypeFilter}
                        onChange={handleFilterChange}
                        label="Content Type"
                        startAdornment={<FilterList sx={{ mr: 1 }} />}
                      >
                        <MenuItem value="all">All Types</MenuItem>
                        <MenuItem value="text">Text</MenuItem>
                        <MenuItem value="json">JSON</MenuItem>
                        <MenuItem value="csv">CSV</MenuItem>
                        <MenuItem value="url">URLs</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} md={2}>
                    <Typography variant="body2" color="text.secondary" align="center">
                      {filteredData.length} results
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Chart Selector */}
          <Grid item xs={12}>
            <ChartSelector
              chartTypes={CHART_TYPES}
              selectedChart={selectedChart}
              onChartChange={handleChartChange}
            />
          </Grid>

          {/* Main Visualization Area */}
          <Grid item xs={12}>
            <Card sx={{ minHeight: selectedChart === 'table' ? 'auto' : '600px' }}>
              <CardContent sx={{ height: '100%' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                  <Typography variant="h6">
                    {CHART_TYPES.find(c => c.id === selectedChart)?.name || 'Visualization'}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Chip
                      label={`${filteredData.length} entries`}
                      color="primary"
                      variant="outlined"
                    />
                    {selectedChart !== 'table' && (
                      <Button
                        size="small"
                        startIcon={<Download />}
                        onClick={() => {
                          // Simple export functionality
                          const svg = document.querySelector('svg')
                          if (svg) {
                            const svgData = new XMLSerializer().serializeToString(svg)
                            const blob = new Blob([svgData], { type: 'image/svg+xml' })
                            const url = URL.createObjectURL(blob)
                            const a = document.createElement('a')
                            a.href = url
                            a.download = `${selectedChart}_chart.svg`
                            a.click()
                            URL.revokeObjectURL(url)
                          }
                        }}
                      >
                        Export
                      </Button>
                    )}
                  </Box>
                </Box>

                {(processedData || selectedChart === 'table') ? (
                  <SimpleChartRenderer
                    data={processedData}
                    rawData={filteredData}
                    chartType={selectedChart}
                  />
                ) : (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
                    <Typography variant="body1" color="text.secondary">
                      {loading ? 'Processing data...' : 'No data to display'}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Collapsible Data Preview */}
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ pb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6">
                    📋 Raw Data Preview
                  </Typography>
                  <IconButton
                    onClick={() => setShowDataPreview(!showDataPreview)}
                    size="small"
                  >
                    {showDataPreview ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Box>

                <Collapse in={showDataPreview}>
                  <Box sx={{ mt: 2 }}>
                    <DataPreview
                      data={filteredData.slice(0, 10)}
                      onRefresh={handleRefresh}
                      searchTerm={searchTerm}
                      totalCount={clipboardData.length}
                      filteredCount={filteredData.length}
                    />
                  </Box>
                </Collapse>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        )}

        {/* Interactive Dashboard Tab */}
        {currentTab === 1 && (
          <InteractiveClipboardDashboard clipboardData={clipboardData} />
        )}

        {/* Enhanced Dashboard Tab */}
        {currentTab === 2 && (
          <EnhancedClipboardDashboard clipboardData={clipboardData} />
        )}

        {/* Memory Protection Dashboard Tab */}
        {currentTab === 3 && (
          <ImprovedMemoryDashboard />
        )}

        {/* Database Management Tab */}
        {currentTab === 4 && (
          <DatabaseManager />
        )}

        {/* Clipboard CRUD Management Tab */}
        {currentTab === 5 && (
          <SimpleClipboardCRUD />
        )}
      </Container>

      {/* Speed Dial for Quick Actions */}
      <SpeedDial
        ariaLabel="Quick Actions"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        {speedDialActions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={action.onClick}
          />
        ))}
      </SpeedDial>

      {/* Loading Backdrop */}
      <Backdrop sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }} open={loading}>
        <CircularProgress color="inherit" />
      </Backdrop>

      {/* Success Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
      >
        <Alert onClose={() => setSnackbarOpen(false)} severity="success">
          Clipboard data loaded successfully!
        </Alert>
      </Snackbar>

      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default App
