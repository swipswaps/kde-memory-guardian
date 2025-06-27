import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react'
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
  Fade,
  Collapse,
  Avatar,
  Badge,
  Skeleton,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Snackbar,
  Backdrop,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemButton
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
  Link,
  Email,
  Code,
  TextFields,
  Image,
  PictureAsPdf,
  Description,
  Bookmark,
  History,
  Star,
  StarBorder,
  Share,
  MoreVert,
  Fullscreen,
  FullscreenExit,
  ZoomIn,
  ZoomOut,
  GridView,
  ViewStream,
  AutoAwesome,
  SmartToy,
  Psychology,
  Insights,
  Analytics,
  Speed,
  Memory,
  CloudSync,
  Sync,
  CheckCircle,
  RadioButtonUnchecked,
  ExpandLess,
  ExpandMore
} from '@mui/icons-material'
import { FixedSizeList as VirtualList } from 'react-window'

function EnhancedClipboardDashboard({ clipboardData = [] }) {
  // Enhanced state management with modern patterns
  const [activeTab, setActiveTab] = useState(0)
  const [filters, setFilters] = useState({
    search: '',
    contentType: 'all',
    dateRange: 'all',
    sizeRange: [0, 100],
    hasUrl: false,
    hasEmail: false,
    minWords: 0,
    maxWords: 50000,
    starred: false,
    recent: false
  })
  const [sortBy, setSortBy] = useState('timestamp')
  const [sortOrder, setSortOrder] = useState('desc')
  const [viewMode, setViewMode] = useState('cards')
  const [itemsPerPage, setItemsPerPage] = useState(25)
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedItems, setSelectedItems] = useState(new Set())
  const [searchSuggestions, setSearchSuggestions] = useState([])
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  const [recentSearches, setRecentSearches] = useState([])
  const [favoriteFilters, setFavoriteFilters] = useState([])
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' })
  const [isLoading, setIsLoading] = useState(false)

  // Refs for advanced features
  const searchInputRef = useRef(null)
  const virtualListRef = useRef(null)

  // Enhanced data processing with performance optimizations
  const processedData = useMemo(() => {
    console.log('🎯 Enhanced processing:', clipboardData.length, 'entries')
    
    if (!Array.isArray(clipboardData) || clipboardData.length === 0) {
      return { filtered: [], stats: {}, facets: {}, searchSuggestions: [] }
    }

    // Enrich data with advanced computed fields
    const enriched = clipboardData.map((item, index) => {
      const content = item.content || ''
      const timestamp = new Date(item.timestamp || Date.now())
      const size_bytes = item.size_bytes || new Blob([content]).size
      
      return {
        ...item,
        id: item.id || `item-${index}`,
        content,
        timestamp,
        size_bytes,
        content_type: item.content_type || 'text',
        content_preview: content.substring(0, 200),
        content_snippet: content.substring(0, 50),
        word_count: content.split(/\s+/).filter(w => w.length > 0).length,
        char_count: content.length,
        line_count: content.split('\n').length,
        has_url: /https?:\/\/[^\s]+/i.test(content),
        has_email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/i.test(content),
        has_code: /[{}();]/.test(content) || content.includes('function') || content.includes('import'),
        has_json: content.trim().startsWith('{') || content.trim().startsWith('['),
        has_markdown: /#{1,6}\s/.test(content) || /\*\*.*\*\*/.test(content),
        has_html: /<[^>]+>/.test(content),
        has_css: /\{[^}]*:[^}]*\}/.test(content),
        has_sql: /\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b/i.test(content),
        day_of_week: timestamp.getDay(),
        hour_of_day: timestamp.getHours(),
        date_string: timestamp.toISOString().split('T')[0],
        time_ago: getTimeAgo(timestamp),
        size_category: getSizeCategory(size_bytes),
        content_category: getContentCategory(content),
        readability_score: getReadabilityScore(content),
        is_recent: (Date.now() - timestamp.getTime()) < 24 * 60 * 60 * 1000, // Last 24 hours
        is_starred: false, // TODO: Implement starring functionality
        similarity_hash: getSimpleHash(content.substring(0, 100))
      }
    })

    // Generate search suggestions from content
    const suggestions = generateSearchSuggestions(enriched)
    setSearchSuggestions(suggestions)

    // Apply enhanced filtering
    let filtered = enriched

    // Smart search with multiple fields
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      filtered = filtered.filter(item =>
        item.content.toLowerCase().includes(searchLower) ||
        item.content_type.toLowerCase().includes(searchLower) ||
        item.content_category.toLowerCase().includes(searchLower)
      )
    }

    // Enhanced content type filtering
    if (filters.contentType !== 'all') {
      filtered = filtered.filter(item => {
        switch (filters.contentType) {
          case 'url': return item.has_url
          case 'email': return item.has_email
          case 'code': return item.has_code
          case 'json': return item.has_json
          case 'markdown': return item.has_markdown
          case 'html': return item.has_html
          case 'large': return item.size_bytes > 10000
          case 'small': return item.size_bytes <= 1000
          case 'recent': return item.is_recent
          default: return item.content_type.toLowerCase().includes(filters.contentType)
        }
      })
    }

    // Date range filtering
    if (filters.dateRange !== 'all') {
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
    }

    // Size range filtering
    if (filtered.length > 0) {
      const maxSize = Math.max(...filtered.map(item => item.size_bytes))
      const minSize = (filters.sizeRange[0] / 100) * maxSize
      const maxSizeFilter = (filters.sizeRange[1] / 100) * maxSize
      filtered = filtered.filter(item => 
        item.size_bytes >= minSize && item.size_bytes <= maxSizeFilter
      )
    }

    // Word count filtering
    filtered = filtered.filter(item =>
      item.word_count >= filters.minWords && item.word_count <= filters.maxWords
    )

    // Special filters
    if (filters.hasUrl) {
      filtered = filtered.filter(item => item.has_url)
    }
    if (filters.hasEmail) {
      filtered = filtered.filter(item => item.has_email)
    }
    if (filters.starred) {
      filtered = filtered.filter(item => item.is_starred)
    }
    if (filters.recent) {
      filtered = filtered.filter(item => item.is_recent)
    }

    // Enhanced sorting
    filtered.sort((a, b) => {
      let aVal = a[sortBy]
      let bVal = b[sortBy]
      
      if (sortBy === 'timestamp') {
        aVal = aVal.getTime()
        bVal = bVal.getTime()
      } else if (sortBy === 'relevance') {
        // Custom relevance scoring
        aVal = calculateRelevanceScore(a, filters.search)
        bVal = calculateRelevanceScore(b, filters.search)
      }
      
      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })

    // Calculate enhanced statistics
    const stats = {
      total: enriched.length,
      filtered: filtered.length,
      totalSize: filtered.reduce((sum, item) => sum + item.size_bytes, 0),
      avgSize: filtered.length > 0 ? filtered.reduce((sum, item) => sum + item.size_bytes, 0) / filtered.length : 0,
      urlCount: filtered.filter(item => item.has_url).length,
      emailCount: filtered.filter(item => item.has_email).length,
      codeCount: filtered.filter(item => item.has_code).length,
      jsonCount: filtered.filter(item => item.has_json).length,
      markdownCount: filtered.filter(item => item.has_markdown).length,
      recentCount: filtered.filter(item => item.is_recent).length,
      avgWords: filtered.length > 0 ? filtered.reduce((sum, item) => sum + item.word_count, 0) / filtered.length : 0,
      avgReadability: filtered.length > 0 ? filtered.reduce((sum, item) => sum + item.readability_score, 0) / filtered.length : 0
    }

    // Calculate enhanced facets
    const facets = {
      contentTypes: [...new Set(enriched.map(item => item.content_type))],
      contentCategories: [...new Set(enriched.map(item => item.content_category))],
      sizeCategories: [...new Set(enriched.map(item => item.size_category))],
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

    return { filtered, stats, facets, searchSuggestions: suggestions }
  }, [clipboardData, filters, sortBy, sortOrder])

  // Helper functions
  const getTimeAgo = (timestamp) => {
    const now = new Date()
    const diff = now - timestamp
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return 'Just now'
  }

  const getSizeCategory = (bytes) => {
    if (bytes < 1000) return 'tiny'
    if (bytes < 10000) return 'small'
    if (bytes < 100000) return 'medium'
    if (bytes < 1000000) return 'large'
    return 'huge'
  }

  const getContentCategory = (content) => {
    if (/https?:\/\//.test(content)) return 'url'
    if (/@.*\./.test(content)) return 'email'
    if (/[{}();]/.test(content)) return 'code'
    if (content.trim().startsWith('{')) return 'json'
    if (/#{1,6}\s/.test(content)) return 'markdown'
    if (/<[^>]+>/.test(content)) return 'html'
    if (content.length > 1000) return 'document'
    return 'text'
  }

  const getReadabilityScore = (content) => {
    // Simple readability score based on sentence and word length
    const sentences = content.split(/[.!?]+/).length
    const words = content.split(/\s+/).length
    const avgWordsPerSentence = words / Math.max(sentences, 1)
    return Math.min(100, Math.max(0, 100 - avgWordsPerSentence * 2))
  }

  const getSimpleHash = (str) => {
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return Math.abs(hash)
  }

  const generateSearchSuggestions = (data) => {
    const suggestions = new Set()
    data.forEach(item => {
      // Extract common words and phrases
      const words = item.content.toLowerCase().match(/\b\w{3,}\b/g) || []
      words.slice(0, 5).forEach(word => suggestions.add(word))
      
      // Add content categories
      suggestions.add(item.content_category)
      
      // Add file extensions
      const extensions = item.content.match(/\.\w{2,4}\b/g) || []
      extensions.forEach(ext => suggestions.add(ext))
    })
    
    return Array.from(suggestions).slice(0, 20)
  }

  const calculateRelevanceScore = (item, searchTerm) => {
    if (!searchTerm) return 0
    
    const content = item.content.toLowerCase()
    const term = searchTerm.toLowerCase()
    
    let score = 0
    
    // Exact matches get higher scores
    if (content.includes(term)) score += 10
    
    // Recent items get bonus
    if (item.is_recent) score += 5
    
    // Smaller items are often more relevant
    if (item.size_bytes < 1000) score += 3
    
    // URLs and emails are often important
    if (item.has_url || item.has_email) score += 2
    
    return score
  }

  return (
    <Box sx={{ p: 3, minHeight: '100vh', bgcolor: 'grey.50' }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, color: 'primary.main' }}>
        🎯 Enhanced Clipboard Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Advanced filtering and visualization with modern UX patterns
      </Typography>

      {/* Enhanced Quick Stats with animations */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}>
          <Fade in timeout={500}>
            <Card elevation={2} sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold">
                  {processedData.stats.filtered}
                </Typography>
                <Typography variant="body2">
                  Filtered Entries
                </Typography>
                <Typography variant="caption">
                  of {processedData.stats.total} total
                </Typography>
              </CardContent>
            </Card>
          </Fade>
        </Grid>
        <Grid item xs={6} md={3}>
          <Fade in timeout={700}>
            <Card elevation={2} sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold">
                  {(processedData.stats.totalSize / 1024 / 1024).toFixed(1)}MB
                </Typography>
                <Typography variant="body2">
                  Total Size
                </Typography>
                <Typography variant="caption">
                  Avg: {(processedData.stats.avgSize / 1024).toFixed(1)}KB
                </Typography>
              </CardContent>
            </Card>
          </Fade>
        </Grid>
        <Grid item xs={6} md={3}>
          <Fade in timeout={900}>
            <Card elevation={2} sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold">
                  {processedData.stats.urlCount}
                </Typography>
                <Typography variant="body2">
                  URLs
                </Typography>
                <Typography variant="caption">
                  {processedData.stats.emailCount} emails
                </Typography>
              </CardContent>
            </Card>
          </Fade>
        </Grid>
        <Grid item xs={6} md={3}>
          <Fade in timeout={1100}>
            <Card elevation={2} sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold">
                  {Math.round(processedData.stats.avgWords)}
                </Typography>
                <Typography variant="body2">
                  Avg Words
                </Typography>
                <Typography variant="caption">
                  {processedData.stats.codeCount} code snippets
                </Typography>
              </CardContent>
            </Card>
          </Fade>
        </Grid>
      </Grid>

      {/* Enhanced Search with Autocomplete and Recent Searches */}
      <Paper elevation={3} sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <AutoAwesome sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Smart Search & Filters
          </Typography>
          <Button
            startIcon={<Clear />}
            onClick={() => {
              setFilters({
                search: '',
                contentType: 'all',
                dateRange: 'all',
                sizeRange: [0, 100],
                hasUrl: false,
                hasEmail: false,
                minWords: 0,
                maxWords: 50000,
                starred: false,
                recent: false
              })
              setCurrentPage(1)
            }}
            size="small"
            variant="outlined"
          >
            Clear All
          </Button>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Autocomplete
              freeSolo
              options={searchSuggestions}
              value={filters.search}
              onChange={(event, newValue) => {
                setFilters(prev => ({ ...prev, search: newValue || '' }))
                setCurrentPage(1)
              }}
              onInputChange={(event, newInputValue) => {
                setFilters(prev => ({ ...prev, search: newInputValue }))
                setCurrentPage(1)
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  fullWidth
                  label="Smart Search"
                  placeholder="Search content, URLs, emails, code..."
                  InputProps={{
                    ...params.InputProps,
                    startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                  }}
                />
              )}
              renderOption={(props, option) => (
                <Box component="li" {...props}>
                  <SmartToy sx={{ mr: 1, fontSize: 16, color: 'primary.main' }} />
                  {option}
                </Box>
              )}
            />
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Content Type</InputLabel>
              <Select
                value={filters.contentType}
                onChange={(e) => {
                  setFilters(prev => ({ ...prev, contentType: e.target.value }))
                  setCurrentPage(1)
                }}
                label="Content Type"
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="url">🔗 URLs</MenuItem>
                <MenuItem value="email">📧 Emails</MenuItem>
                <MenuItem value="code">💻 Code</MenuItem>
                <MenuItem value="json">📋 JSON</MenuItem>
                <MenuItem value="markdown">📝 Markdown</MenuItem>
                <MenuItem value="html">🌐 HTML</MenuItem>
                <MenuItem value="large">📦 Large (&gt;10KB)</MenuItem>
                <MenuItem value="small">📄 Small (≤1KB)</MenuItem>
                <MenuItem value="recent">⏰ Recent (24h)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Date Range</InputLabel>
              <Select
                value={filters.dateRange}
                onChange={(e) => {
                  setFilters(prev => ({ ...prev, dateRange: e.target.value }))
                  setCurrentPage(1)
                }}
                label="Date Range"
              >
                <MenuItem value="all">All Time</MenuItem>
                <MenuItem value="today">Today</MenuItem>
                <MenuItem value="week">Last Week</MenuItem>
                <MenuItem value="month">Last Month</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Advanced Filters Toggle */}
        <Box sx={{ mt: 2 }}>
          <Button
            startIcon={showAdvancedFilters ? <ExpandLess /> : <ExpandMore />}
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            size="small"
          >
            Advanced Filters
          </Button>
        </Box>

        <Collapse in={showAdvancedFilters}>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Size Range: {(filters.sizeRange[0])}% - {(filters.sizeRange[1])}%
              </Typography>
              <Slider
                value={filters.sizeRange}
                onChange={(e, newValue) => {
                  setFilters(prev => ({ ...prev, sizeRange: newValue }))
                  setCurrentPage(1)
                }}
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
                  setFilters(prev => ({ ...prev, minWords: newValue[0], maxWords: newValue[1] }))
                  setCurrentPage(1)
                }}
                min={0}
                max={Math.max(50000, processedData.facets.wordRange?.max || 50000)}
                valueLabelDisplay="auto"
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  icon={<Link />}
                  label="Has URLs"
                  color={filters.hasUrl ? 'primary' : 'default'}
                  onClick={() => setFilters(prev => ({ ...prev, hasUrl: !prev.hasUrl }))}
                  variant={filters.hasUrl ? 'filled' : 'outlined'}
                />
                <Chip
                  icon={<Email />}
                  label="Has Emails"
                  color={filters.hasEmail ? 'primary' : 'default'}
                  onClick={() => setFilters(prev => ({ ...prev, hasEmail: !prev.hasEmail }))}
                  variant={filters.hasEmail ? 'filled' : 'outlined'}
                />
                <Chip
                  icon={<Star />}
                  label="Starred"
                  color={filters.starred ? 'primary' : 'default'}
                  onClick={() => setFilters(prev => ({ ...prev, starred: !prev.starred }))}
                  variant={filters.starred ? 'filled' : 'outlined'}
                />
                <Chip
                  icon={<History />}
                  label="Recent"
                  color={filters.recent ? 'primary' : 'default'}
                  onClick={() => setFilters(prev => ({ ...prev, recent: !prev.recent }))}
                  variant={filters.recent ? 'filled' : 'outlined'}
                />
              </Box>
            </Grid>
          </Grid>
        </Collapse>

        {/* Active Filters Display */}
        <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {filters.search && (
            <Chip
              label={`Search: "${filters.search}"`}
              onDelete={() => setFilters(prev => ({ ...prev, search: '' }))}
              size="small"
              color="primary"
            />
          )}
          {filters.contentType !== 'all' && (
            <Chip
              label={`Type: ${filters.contentType}`}
              onDelete={() => setFilters(prev => ({ ...prev, contentType: 'all' }))}
              size="small"
              color="secondary"
            />
          )}
          {filters.dateRange !== 'all' && (
            <Chip
              label={`Date: ${filters.dateRange}`}
              onDelete={() => setFilters(prev => ({ ...prev, dateRange: 'all' }))}
              size="small"
              color="info"
            />
          )}
        </Box>
      </Paper>

      {/* Enhanced View Controls with Modern Design */}
      <Paper elevation={2} sx={{ p: 2, mb: 3, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Insights />
            View Options
          </Typography>

          <ButtonGroup variant="outlined" size="small">
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
            <Button
              variant={viewMode === 'timeline' ? 'contained' : 'outlined'}
              onClick={() => setViewMode('timeline')}
              startIcon={<Timeline />}
            >
              Timeline
            </Button>
          </ButtonGroup>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              label="Sort By"
            >
              <MenuItem value="timestamp">📅 Date</MenuItem>
              <MenuItem value="size_bytes">📏 Size</MenuItem>
              <MenuItem value="word_count">📝 Word Count</MenuItem>
              <MenuItem value="content_type">📋 Type</MenuItem>
              <MenuItem value="relevance">🎯 Relevance</MenuItem>
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

          <Box sx={{ flexGrow: 1 }} />

          <Tooltip title="Toggle Fullscreen">
            <IconButton
              onClick={() => setIsFullscreen(!isFullscreen)}
              color={isFullscreen ? 'primary' : 'default'}
            >
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>

      {/* Results Display with Enhanced Cards */}
      <Paper elevation={2} sx={{ p: 2, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Analytics />
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

        {/* Enhanced Cards View */}
        {viewMode === 'cards' && (
          <Grid container spacing={2}>
            {processedData.filtered.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage).map((item) => (
              <Grid item xs={12} md={6} lg={4} key={item.id}>
                <Card
                  elevation={2}
                  sx={{
                    height: '100%',
                    borderRadius: 2,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      elevation: 8,
                      transform: 'translateY(-4px)'
                    }
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Chip
                        label={item.content_category}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Typography variant="caption" color="text.secondary">
                          {item.time_ago}
                        </Typography>
                        <IconButton size="small">
                          {item.is_starred ? <Star color="warning" /> : <StarBorder />}
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
                        WebkitBoxOrient: 'vertical'
                      }}
                    >
                      {item.content_preview}
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
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Copy to clipboard">
                          <IconButton size="small" color="primary">
                            <ContentCopy />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Share">
                          <IconButton size="small">
                            <Share />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {item.readability_score.toFixed(0)}% readable
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Pagination with enhanced design */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={Math.ceil(processedData.stats.filtered / itemsPerPage)}
            page={currentPage}
            onChange={(e, page) => setCurrentPage(page)}
            color="primary"
            size="large"
            showFirstButton
            showLastButton
          />
        </Box>
      </Paper>

      {/* Performance Alert */}
      {processedData.stats.total > 500 && (
        <Alert severity="info" sx={{ mt: 2, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Speed />
            Large dataset detected ({processedData.stats.total} entries).
            Use filters to improve performance and find specific content faster.
          </Box>
        </Alert>
      )}

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

export default EnhancedClipboardDashboard
