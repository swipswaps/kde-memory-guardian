import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import Fuse from 'fuse.js'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Grid,
  Card,
  CardContent,
  Button,
  ButtonGroup,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Autocomplete,
  Pagination,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Modal,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextareaAutosize,
  Menu,
  MenuList,
  Popper,
  ClickAwayListener,
  Grow,
  ListItemIcon,
  ListItemText,
  Snackbar
} from '@mui/material'
import {
  Search,
  FilterList,
  Clear,
  Download,
  Refresh,
  ViewList,
  ViewModule,
  Timeline,
  BarChart,
  ScatterPlot,
  TableChart,
  TrendingUp,
  Category,
  DateRange,
  Storage,
  ContentCopy,
  Share,
  OpenInNew,
  Close,
  Fullscreen,
  FullscreenExit,
  FindInPage,
  SaveAlt,
  CloudUpload,
  Edit,
  MoreVert
} from '@mui/icons-material'

function InteractiveClipboardDashboard({ clipboardData = [] }) {
  // Enhanced state management
  const [activeTab, setActiveTab] = useState(0)
  const [filters, setFilters] = useState({
    search: '',
    contentType: 'all',
    dateRange: 'all',
    sizeRange: [0, 100],
    hasUrl: false,
    hasEmail: false,
    minWords: 0,
    maxWords: 50000  // Much higher default to avoid filtering out large entries
  })
  const [sortBy, setSortBy] = useState('timestamp')
  const [sortOrder, setSortOrder] = useState('desc')
  const [viewMode, setViewMode] = useState('cards')
  const [itemsPerPage, setItemsPerPage] = useState(25)
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedCard, setSelectedCard] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [contextMenu, setContextMenu] = useState(null)
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' })

  // Ref for search input to maintain focus
  const searchInputRef = useRef(null)

  // Advanced data processing with better performance
  const processedData = useMemo(() => {
    console.log('=== DEBUGGING CLIPBOARD DATA ===')
    console.log('clipboardData type:', typeof clipboardData)
    console.log('clipboardData isArray:', Array.isArray(clipboardData))
    console.log('clipboardData length:', clipboardData?.length)
    console.log('clipboardData sample:', clipboardData?.slice(0, 2))

    if (!Array.isArray(clipboardData) || clipboardData.length === 0) {
      console.log('❌ No clipboard data available or not an array')
      return { filtered: [], stats: {}, facets: {} }
    }

    console.log('✅ Processing clipboard data:', clipboardData.length, 'entries')

    // Enrich data with computed fields
    const enriched = clipboardData.map((item, index) => {
      const content = item.content || ''
      const timestamp = new Date(item.timestamp || Date.now())
      const size_bytes = item.size_bytes || new Blob([content]).size

      const enrichedItem = {
        ...item,
        id: item.id || `item-${index}`,
        content,
        timestamp,
        size_bytes,
        content_type: item.content_type || 'text',
        content_preview: content.substring(0, 150),
        word_count: content.split(/\s+/).filter(w => w.length > 0).length,
        char_count: content.length,
        has_url: /https?:\/\/[^\s]+/i.test(content),
        has_email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/i.test(content),
        has_code: /[{}();]/.test(content) || content.includes('function') || content.includes('import'),
        day_of_week: timestamp.getDay(),
        hour_of_day: timestamp.getHours(),
        date_string: timestamp.toISOString().split('T')[0]
      }

      // Debug first few items
      if (index < 3) {
        console.log(`Item ${index}:`, {
          id: enrichedItem.id,
          word_count: enrichedItem.word_count,
          size_bytes: enrichedItem.size_bytes,
          timestamp: enrichedItem.timestamp,
          content_preview: enrichedItem.content_preview
        })
      }

      return enrichedItem
    })

    console.log('Enriched data length:', enriched.length)

    // Apply filters with debugging
    let filtered = enriched
    console.log('🔧 Starting filtering with', enriched.length, 'entries')

    // Fuzzy Search filter
    if (filters.search) {
      console.log('🔍 Applying fuzzy search filter:', filters.search)
      const beforeSearch = filtered.length

      // Configure Fuse.js for fuzzy search
      const fuseOptions = {
        keys: [
          { name: 'content', weight: 0.7 },
          { name: 'content_type', weight: 0.2 },
          { name: 'content_preview', weight: 0.1 }
        ],
        threshold: 0.4, // Lower = more strict, Higher = more fuzzy
        distance: 100,
        includeScore: true,
        includeMatches: true,
        minMatchCharLength: 2
      }

      const fuse = new Fuse(filtered, fuseOptions)
      const searchResults = fuse.search(filters.search)

      // Extract items from Fuse results and add match info
      filtered = searchResults.map(result => ({
        ...result.item,
        _fuseScore: result.score,
        _fuseMatches: result.matches
      }))

      console.log(`🔍 Fuzzy search filter: ${beforeSearch} → ${filtered.length} entries`)
      console.log('🎯 Sample fuzzy scores:', filtered.slice(0, 3).map(item => ({
        id: item.id,
        score: item._fuseScore?.toFixed(3),
        preview: item.content_preview.substring(0, 50)
      })))
    }

    // Content type filter
    if (filters.contentType !== 'all') {
      console.log('📊 Applying content type filter:', filters.contentType)
      const beforeType = filtered.length
      filtered = filtered.filter(item => {
        switch (filters.contentType) {
          case 'url': return item.has_url
          case 'email': return item.has_email
          case 'code': return item.has_code
          case 'large': return item.size_bytes > 10000
          case 'small': return item.size_bytes <= 1000
          default: return item.content_type.toLowerCase().includes(filters.contentType)
        }
      })
      console.log(`📊 Content type filter: ${beforeType} → ${filtered.length} entries`)
    }

    // Date range filter
    if (filters.dateRange !== 'all') {
      console.log('📅 Applying date range filter:', filters.dateRange)
      const beforeDate = filtered.length
      const now = new Date()
      let cutoff
      switch (filters.dateRange) {
        case 'today':
          cutoff = new Date(now.getFullYear(), now.getMonth(), now.getDate())
          break
        case 'week':
          cutoff = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          break
        case 'month':
          cutoff = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          break
        default:
          cutoff = null
      }
      if (cutoff) {
        filtered = filtered.filter(item => item.timestamp >= cutoff)
      }
      console.log(`📅 Date range filter: ${beforeDate} → ${filtered.length} entries`)
    }

    // Size range filter
    if (filtered.length > 0) {
      console.log('📏 Applying size range filter:', filters.sizeRange)
      const beforeSize = filtered.length
      const maxSize = Math.max(...filtered.map(item => item.size_bytes))
      const minSize = (filters.sizeRange[0] / 100) * maxSize
      const maxSizeFilter = (filters.sizeRange[1] / 100) * maxSize
      console.log(`📏 Size range: ${minSize} - ${maxSizeFilter} bytes (${filters.sizeRange[0]}% - ${filters.sizeRange[1]}%)`)
      filtered = filtered.filter(item =>
        item.size_bytes >= minSize && item.size_bytes <= maxSizeFilter
      )
      console.log(`📏 Size range filter: ${beforeSize} → ${filtered.length} entries`)
    }

    // Word count filter
    console.log('📝 Applying word count filter:', filters.minWords, '-', filters.maxWords)
    const beforeWords = filtered.length
    if (filtered.length > 0) {
      console.log('📝 Sample word counts:', filtered.slice(0, 3).map(item => ({ id: item.id, word_count: item.word_count })))
    }
    filtered = filtered.filter(item =>
      item.word_count >= filters.minWords && item.word_count <= filters.maxWords
    )
    console.log(`📝 Word count filter: ${beforeWords} → ${filtered.length} entries`)

    // URL/Email filters
    if (filters.hasUrl) {
      console.log('🔗 Applying URL filter')
      const beforeUrl = filtered.length
      filtered = filtered.filter(item => item.has_url)
      console.log(`🔗 URL filter: ${beforeUrl} → ${filtered.length} entries`)
    }
    if (filters.hasEmail) {
      console.log('📧 Applying email filter')
      const beforeEmail = filtered.length
      filtered = filtered.filter(item => item.has_email)
      console.log(`📧 Email filter: ${beforeEmail} → ${filtered.length} entries`)
    }

    // Sorting
    filtered.sort((a, b) => {
      let aVal = a[sortBy]
      let bVal = b[sortBy]

      if (sortBy === 'timestamp') {
        aVal = aVal.getTime()
        bVal = bVal.getTime()
      }

      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })

    console.log('✅ Final filtered results:', filtered.length, 'entries')

    // Calculate statistics
    const stats = {
      total: enriched.length,
      filtered: filtered.length,
      totalSize: filtered.reduce((sum, item) => sum + item.size_bytes, 0),
      avgSize: filtered.length > 0 ? filtered.reduce((sum, item) => sum + item.size_bytes, 0) / filtered.length : 0,
      urlCount: filtered.filter(item => item.has_url).length,
      emailCount: filtered.filter(item => item.has_email).length,
      codeCount: filtered.filter(item => item.has_code).length,
      avgWords: filtered.length > 0 ? filtered.reduce((sum, item) => sum + item.word_count, 0) / filtered.length : 0
    }

    // Calculate facets for filtering
    const facets = {
      contentTypes: [...new Set(enriched.map(item => item.content_type))],
      dateRange: {
        earliest: Math.min(...enriched.map(item => item.timestamp.getTime())),
        latest: Math.max(...enriched.map(item => item.timestamp.getTime()))
      },
      sizeRange: {
        min: Math.min(...enriched.map(item => item.size_bytes)),
        max: Math.max(...enriched.map(item => item.size_bytes))
      },
      wordRange: {
        min: Math.min(...enriched.map(item => item.word_count)),
        max: Math.max(...enriched.map(item => item.word_count))
      }
    }

    return { filtered, stats, facets }
  }, [clipboardData, filters, sortBy, sortOrder])

  // Pagination
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return processedData.filtered.slice(startIndex, startIndex + itemsPerPage)
  }, [processedData.filtered, currentPage, itemsPerPage])

  // Filter update functions with stable references to prevent re-renders
  const updateFilter = useCallback((key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setCurrentPage(1) // Reset to first page when filtering
  }, [])

  // Local search state to prevent focus loss
  const [searchValue, setSearchValue] = useState(filters.search)

  // Debounced search effect
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setFilters(prev => ({ ...prev, search: searchValue }))
      setCurrentPage(1)
    }, 300) // 300ms debounce

    return () => clearTimeout(timeoutId)
  }, [searchValue])

  // Separate search handler to prevent focus loss
  const handleSearchChange = useCallback((event) => {
    setSearchValue(event.target.value)
  }, [])

  const clearFilters = () => {
    setFilters({
      search: '',
      contentType: 'all',
      dateRange: 'all',
      sizeRange: [0, 100],
      hasUrl: false,
      hasEmail: false,
      minWords: 0,
      maxWords: 50000  // Much higher default to avoid filtering out large entries
    })
    setSearchValue('') // Also clear local search state
    setCurrentPage(1)
  }

  // Enhanced utility functions
  const highlightSearchText = (text, searchTerm) => {
    if (!searchTerm) return text

    const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
    return text.replace(regex, '<mark style="background-color: #ffeb3b; padding: 2px 4px; border-radius: 2px;">$1</mark>')
  }

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      setSnackbar({ open: true, message: 'Copied to clipboard!', severity: 'success' })
    } catch (err) {
      setSnackbar({ open: true, message: 'Failed to copy to clipboard', severity: 'error' })
    }
  }

  const openWebSearch = (text) => {
    const query = encodeURIComponent(text.substring(0, 100))
    window.open(`https://www.google.com/search?q=${query}`, '_blank')
  }

  const handleCardClick = (item) => {
    setSelectedCard(item)
    setModalOpen(true)
  }

  const handleContextMenu = (event, item) => {
    event.preventDefault()
    setContextMenu({
      mouseX: event.clientX - 2,
      mouseY: event.clientY - 4,
      item: item
    })
  }

  const handleCloseContextMenu = () => {
    setContextMenu(null)
  }

  // Enhanced Card Modal Component
  const CardModal = () => {
    if (!selectedCard) return null

    const highlightedContent = highlightSearchText(selectedCard.content, filters.search)

    return (
      <Dialog
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, maxHeight: '90vh' }
        }}
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip label={selectedCard.content_type} size="small" color="primary" />
            <Typography variant="h6">Clipboard Entry Details</Typography>
          </Box>
          <IconButton onClick={() => setModalOpen(false)} size="small">
            <Close />
          </IconButton>
        </DialogTitle>

        <DialogContent dividers>
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Size:</Typography>
              <Typography variant="body2">{(selectedCard.size_bytes / 1024).toFixed(1)}KB</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Words:</Typography>
              <Typography variant="body2">{selectedCard.word_count}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Created:</Typography>
              <Typography variant="body2">{selectedCard.timestamp.toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Type:</Typography>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                {selectedCard.has_url && <Chip label="URL" size="small" color="info" />}
                {selectedCard.has_email && <Chip label="Email" size="small" color="success" />}
                {selectedCard.has_code && <Chip label="Code" size="small" color="warning" />}
              </Box>
            </Grid>
          </Grid>

          <Typography variant="subtitle2" gutterBottom>Content:</Typography>
          <Paper
            variant="outlined"
            sx={{
              p: 2,
              maxHeight: 400,
              overflow: 'auto',
              bgcolor: 'grey.50',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              lineHeight: 1.5
            }}
          >
            <div dangerouslySetInnerHTML={{ __html: highlightedContent }} />
          </Paper>
        </DialogContent>

        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button
            startIcon={<ContentCopy />}
            onClick={() => copyToClipboard(selectedCard.content)}
            variant="contained"
            color="primary"
          >
            Copy to Clipboard
          </Button>
          <Button
            startIcon={<FindInPage />}
            onClick={() => openWebSearch(selectedCard.content)}
            variant="outlined"
          >
            Web Search
          </Button>
          <Button
            startIcon={<SaveAlt />}
            onClick={() => {
              const blob = new Blob([selectedCard.content], { type: 'text/plain' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `clipboard-${selectedCard.id}.txt`
              a.click()
              URL.revokeObjectURL(url)
            }}
            variant="outlined"
          >
            Save as File
          </Button>
          <Button
            startIcon={<Share />}
            onClick={() => {
              if (navigator.share) {
                navigator.share({
                  title: 'Clipboard Content',
                  text: selectedCard.content
                })
              } else {
                copyToClipboard(selectedCard.content)
              }
            }}
            variant="outlined"
          >
            Share
          </Button>
        </DialogActions>
      </Dialog>
    )
  }

  // Context Menu Component
  const ContextMenuComponent = () => (
    <Menu
      open={contextMenu !== null}
      onClose={handleCloseContextMenu}
      anchorReference="anchorPosition"
      anchorPosition={
        contextMenu !== null
          ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
          : undefined
      }
    >
      <MenuItem onClick={() => {
        copyToClipboard(contextMenu.item.content)
        handleCloseContextMenu()
      }}>
        <ListItemIcon><ContentCopy fontSize="small" /></ListItemIcon>
        <ListItemText>Copy to Clipboard</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => {
        handleCardClick(contextMenu.item)
        handleCloseContextMenu()
      }}>
        <ListItemIcon><OpenInNew fontSize="small" /></ListItemIcon>
        <ListItemText>View Details</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => {
        openWebSearch(contextMenu.item.content)
        handleCloseContextMenu()
      }}>
        <ListItemIcon><FindInPage fontSize="small" /></ListItemIcon>
        <ListItemText>Web Search</ListItemText>
      </MenuItem>
    </Menu>
  )

  // Quick Stats Component
  const QuickStats = () => (
    <Grid container spacing={2} sx={{ mb: 3 }}>
      <Grid item xs={6} md={3}>
        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="primary">
              {processedData.stats.filtered}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Filtered Entries
            </Typography>
            <Typography variant="caption">
              of {processedData.stats.total} total
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={6} md={3}>
        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="secondary">
              {(processedData.stats.totalSize / 1024 / 1024).toFixed(1)}MB
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Size
            </Typography>
            <Typography variant="caption">
              Avg: {(processedData.stats.avgSize / 1024).toFixed(1)}KB
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={6} md={3}>
        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="success.main">
              {processedData.stats.urlCount}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              URLs
            </Typography>
            <Typography variant="caption">
              {processedData.stats.emailCount} emails
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={6} md={3}>
        <Card>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="warning.main">
              {Math.round(processedData.stats.avgWords)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Avg Words
            </Typography>
            <Typography variant="caption">
              {processedData.stats.codeCount} code snippets
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  // Advanced Filters Component
  const AdvancedFilters = () => (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <FilterList sx={{ mr: 1 }} />
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Advanced Filters
        </Typography>
        <Button
          startIcon={<Clear />}
          onClick={clearFilters}
          size="small"
        >
          Clear All
        </Button>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <TextField
            ref={searchInputRef}
            fullWidth
            label="Search Content (Fuzzy Search Enabled)"
            placeholder="Try: 'clipbord', 'javascrpt', 'functio'..."
            value={searchValue}
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
            }}
            autoComplete="off"
            variant="outlined"
            autoFocus={false}
            helperText={searchValue ? `Fuzzy searching for "${searchValue}"... (supports typos)` : "Fuzzy search supports typos and partial matches"}
          />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Content Type</InputLabel>
            <Select
              value={filters.contentType}
              onChange={(e) => updateFilter('contentType', e.target.value)}
              label="Content Type"
            >
              <MenuItem value="all">All Types</MenuItem>
              <MenuItem value="url">URLs Only</MenuItem>
              <MenuItem value="email">Emails Only</MenuItem>
              <MenuItem value="code">Code Snippets</MenuItem>
              <MenuItem value="large">Large Items (&gt;10KB)</MenuItem>
              <MenuItem value="small">Small Items (≤1KB)</MenuItem>
              {processedData.facets.contentTypes?.map(type => (
                <MenuItem key={type} value={type}>{type}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Date Range</InputLabel>
            <Select
              value={filters.dateRange}
              onChange={(e) => updateFilter('dateRange', e.target.value)}
              label="Date Range"
            >
              <MenuItem value="all">All Time</MenuItem>
              <MenuItem value="today">Today</MenuItem>
              <MenuItem value="week">Last Week</MenuItem>
              <MenuItem value="month">Last Month</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography gutterBottom>
            Size Range: {(filters.sizeRange[0])}% - {(filters.sizeRange[1])}%
          </Typography>
          <Slider
            value={filters.sizeRange}
            onChange={(e, newValue) => updateFilter('sizeRange', newValue)}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value}%`}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography gutterBottom>
            Word Count: {filters.minWords} - {filters.maxWords}
          </Typography>
          <Slider
            value={[filters.minWords, filters.maxWords]}
            onChange={(e, newValue) => {
              updateFilter('minWords', newValue[0])
              updateFilter('maxWords', newValue[1])
            }}
            min={0}
            max={Math.max(50000, processedData.facets.wordRange?.max || 50000)}
            valueLabelDisplay="auto"
          />
        </Grid>
      </Grid>

      {/* Active Filters Display */}
      <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {filters.search && (
          <Chip
            label={`Search: "${filters.search}"`}
            onDelete={() => {
              updateFilter('search', '')
              setSearchValue('')
            }}
            size="small"
          />
        )}
        {filters.contentType !== 'all' && (
          <Chip
            label={`Type: ${filters.contentType}`}
            onDelete={() => updateFilter('contentType', 'all')}
            size="small"
          />
        )}
        {filters.dateRange !== 'all' && (
          <Chip
            label={`Date: ${filters.dateRange}`}
            onDelete={() => updateFilter('dateRange', 'all')}
            size="small"
          />
        )}
      </Box>
    </Paper>
  )

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        🎯 Interactive Clipboard Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Advanced filtering and visualization for large clipboard datasets
      </Typography>

      {/* Quick Stats */}
      <QuickStats />

      {/* Advanced Filters */}
      <AdvancedFilters />

      {/* View Controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6">View Options:</Typography>
          
          <ButtonGroup size="small">
            <Button
              variant={viewMode === 'cards' ? 'contained' : 'outlined'}
              onClick={() => setViewMode('cards')}
              startIcon={<ViewModule />}
            >
              Cards
            </Button>
            <Button
              variant={viewMode === 'list' ? 'contained' : 'outlined'}
              onClick={() => setViewMode('list')}
              startIcon={<ViewList />}
            >
              List
            </Button>
            <Button
              variant={viewMode === 'table' ? 'contained' : 'outlined'}
              onClick={() => setViewMode('table')}
              startIcon={<TableChart />}
            >
              Table
            </Button>
          </ButtonGroup>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              label="Sort By"
            >
              <MenuItem value="timestamp">Date</MenuItem>
              <MenuItem value="size_bytes">Size</MenuItem>
              <MenuItem value="word_count">Word Count</MenuItem>
              <MenuItem value="content_type">Type</MenuItem>
            </Select>
          </FormControl>

          <ButtonGroup size="small">
            <Button
              variant={sortOrder === 'desc' ? 'contained' : 'outlined'}
              onClick={() => setSortOrder('desc')}
            >
              ↓ Desc
            </Button>
            <Button
              variant={sortOrder === 'asc' ? 'contained' : 'outlined'}
              onClick={() => setSortOrder('asc')}
            >
              ↑ Asc
            </Button>
          </ButtonGroup>
        </Box>
      </Paper>

      {/* Results Display */}
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Results ({processedData.stats.filtered} of {processedData.stats.total})
          </Typography>
          <FormControl size="small">
            <InputLabel>Per Page</InputLabel>
            <Select
              value={itemsPerPage}
              onChange={(e) => setItemsPerPage(e.target.value)}
              label="Per Page"
            >
              <MenuItem value={10}>10</MenuItem>
              <MenuItem value={25}>25</MenuItem>
              <MenuItem value={50}>50</MenuItem>
              <MenuItem value={100}>100</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Data Display */}
        {viewMode === 'cards' && (
          <Grid container spacing={2}>
            {paginatedData.map((item) => (
              <Grid item xs={12} md={6} lg={4} key={item.id}>
                <Card
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 6,
                      bgcolor: 'action.hover'
                    }
                  }}
                  onClick={() => handleCardClick(item)}
                  onContextMenu={(e) => handleContextMenu(e, item)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Chip
                        label={item.content_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          {item.timestamp.toLocaleDateString()}
                        </Typography>
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation()
                            copyToClipboard(item.content)
                          }}
                          sx={{ opacity: 0.7, '&:hover': { opacity: 1 } }}
                        >
                          <ContentCopy fontSize="small" />
                        </IconButton>
                      </Box>
                    </Box>

                    <Typography
                      variant="body2"
                      sx={{
                        mb: 2,
                        height: 80,
                        overflow: 'hidden',
                        display: '-webkit-box',
                        WebkitLineClamp: 4,
                        WebkitBoxOrient: 'vertical',
                        lineHeight: 1.4
                      }}
                    >
                      {filters.search ? (
                        <span dangerouslySetInnerHTML={{
                          __html: highlightSearchText(item.content_preview, filters.search)
                        }} />
                      ) : (
                        item.content_preview
                      )}...
                    </Typography>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        {(item.size_bytes / 1024).toFixed(1)}KB • {item.word_count} words
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        {item.has_url && <Chip label="URL" size="small" color="info" />}
                        {item.has_email && <Chip label="Email" size="small" color="success" />}
                        {item.has_code && <Chip label="Code" size="small" color="warning" />}
                      </Box>
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        {item._fuseScore ?
                          `Match: ${(100 - item._fuseScore * 100).toFixed(0)}% • Click for details` :
                          'Click to view details'
                        }
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="Copy to clipboard">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation()
                              copyToClipboard(item.content)
                            }}
                          >
                            <ContentCopy fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Web search">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation()
                              openWebSearch(item.content)
                            }}
                          >
                            <FindInPage fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="More options">
                          <IconButton
                            size="small"
                            onClick={(e) => handleContextMenu(e, item)}
                          >
                            <MoreVert fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Pagination */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={Math.ceil(processedData.stats.filtered / itemsPerPage)}
            page={currentPage}
            onChange={(e, page) => setCurrentPage(page)}
            color="primary"
          />
        </Box>
      </Paper>

      {/* Performance Alert */}
      {processedData.stats.total > 500 && (
        <Alert severity="info" sx={{ mt: 2 }}>
          💡 Large dataset detected ({processedData.stats.total} entries).
          Use filters to improve performance and find specific content faster.
        </Alert>
      )}

      {/* Enhanced Card Modal */}
      <CardModal />

      {/* Context Menu */}
      <ContextMenuComponent />

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default InteractiveClipboardDashboard
