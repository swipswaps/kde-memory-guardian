import React, { useMemo, useState } from 'react'
import {
  Box,
  Button,
  IconButton,
  Tooltip,
  Typography,
  Chip,
  Stack,
  Alert,
  Paper,
  Toolbar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Switch,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Checkbox,
  Menu,
  MenuItem as MenuItemComponent,
  Divider,
  Card,
  CardContent,
  Grid
} from '@mui/material'
import {
  Download,
  Refresh,
  FilterList,
  ViewColumn,
  Search,
  Clear,
  ContentCopy,
  Edit,
  Delete,
  Visibility,
  VisibilityOff,
  TableChart,
  GridView,
  List,
  Analytics
} from '@mui/icons-material'
import { format } from 'date-fns'

/**
 * Enhanced Data Table with Custom Implementation
 * Provides professional spreadsheet functionality with advanced features
 */
function EnhancedDataTable({ data, title = "Enhanced Data Table" }) {
  const [globalFilter, setGlobalFilter] = useState('')
  const [orderBy, setOrderBy] = useState('timestamp')
  const [order, setOrder] = useState('desc')
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [selected, setSelected] = useState([])
  const [dense, setDense] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [typeFilter, setTypeFilter] = useState('all')
  const [anchorEl, setAnchorEl] = useState(null)

  // Process and filter data
  const processedData = useMemo(() => {
    if (!data || data.length === 0) return []

    let filtered = data.map((item, index) => ({
      id: item.id || `item_${index}`,
      timestamp: item.timestamp || new Date().toISOString(),
      content_type: item.content_type || 'Unknown',
      content: item.content || '',
      content_preview: item.content ? item.content.substring(0, 100) + (item.content.length > 100 ? '...' : '') : '',
      size_bytes: item.size_bytes || item.content?.length || 0,
      word_count: item.content ? item.content.split(/\s+/).length : 0,
      char_count: item.content?.length || 0,
      formatted_timestamp: item.timestamp ? format(new Date(item.timestamp), 'MMM dd, yyyy HH:mm:ss') : 'Unknown',
      age_minutes: item.timestamp ? Math.round((Date.now() - new Date(item.timestamp).getTime()) / 60000) : 0
    }))

    // Apply type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(item => item.content_type === typeFilter)
    }

    // Apply global filter
    if (globalFilter) {
      filtered = filtered.filter(item =>
        item.content.toLowerCase().includes(globalFilter.toLowerCase()) ||
        item.content_type.toLowerCase().includes(globalFilter.toLowerCase())
      )
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aVal = a[orderBy]
      let bVal = b[orderBy]

      if (orderBy === 'timestamp') {
        aVal = new Date(a.timestamp)
        bVal = new Date(b.timestamp)
      }

      if (order === 'desc') {
        return bVal > aVal ? 1 : -1
      } else {
        return aVal > bVal ? 1 : -1
      }
    })

    return filtered
  }, [data, globalFilter, typeFilter, orderBy, order])

  // Handle sorting
  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc'
    setOrder(isAsc ? 'desc' : 'asc')
    setOrderBy(property)
  }

  // Handle selection
  const handleSelectAllClick = (event) => {
    if (event.target.checked) {
      const newSelected = processedData.map((n) => n.id)
      setSelected(newSelected)
      return
    }
    setSelected([])
  }

  const handleClick = (event, id) => {
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
        selected.slice(selectedIndex + 1),
      )
    }
    setSelected(newSelected)
  }

  const isSelected = (id) => selected.indexOf(id) !== -1

  // Handle pagination
  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  // Export functionality
  const handleExport = () => {
    const csvContent = processedData.map(row =>
      `"${row.id}","${row.formatted_timestamp}","${row.content_type}","${row.content.replace(/"/g, '""')}","${row.size_bytes}"`
    ).join('\n')
    const header = '"ID","Timestamp","Type","Content","Size"\n'
    const blob = new Blob([header + csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'clipboard-data.csv'
    a.click()
  }

  // Get unique content types for filter
  const contentTypes = useMemo(() => {
    const types = [...new Set(data?.map(item => item.content_type) || [])]
    return types.filter(Boolean)
  }, [data])
  if (!data || data.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
        <TableChart sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No Data Available
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Copy some data to your clipboard to see it here
        </Typography>
      </Paper>
    )
  }

  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - processedData.length) : 0

  return (
    <Box sx={{ width: '100%' }}>
      {/* Enhanced Header with Controls */}
      <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              {title}
            </Typography>
            <Stack direction="row" spacing={1}>
              <Chip
                label={`${processedData.length} entries`}
                size="small"
                color="primary"
                variant="outlined"
              />
              <Chip
                label={`${contentTypes.length} types`}
                size="small"
                color="secondary"
                variant="outlined"
              />
              {selected.length > 0 && (
                <Chip
                  label={`${selected.length} selected`}
                  size="small"
                  color="success"
                  variant="filled"
                />
              )}
            </Stack>
          </Grid>
          <Grid item xs={12} md={6}>
            <Stack direction="row" spacing={1} justifyContent="flex-end">
              <TextField
                size="small"
                placeholder="Search content..."
                value={globalFilter}
                onChange={(e) => setGlobalFilter(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Type</InputLabel>
                <Select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  label="Type"
                >
                  <MenuItemComponent value="all">All Types</MenuItemComponent>
                  {contentTypes.map(type => (
                    <MenuItemComponent key={type} value={type}>{type}</MenuItemComponent>
                  ))}
                </Select>
              </FormControl>
              <Button
                startIcon={<Download />}
                variant="outlined"
                size="small"
                onClick={handleExport}
              >
                Export
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>
      {/* Enhanced Table */}
      <Paper elevation={2}>
        <TableContainer>
          <Table sx={{ minWidth: 750 }} size={dense ? 'small' : 'medium'}>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'primary.main' }}>
                <TableCell padding="checkbox">
                  <Checkbox
                    color="default"
                    indeterminate={selected.length > 0 && selected.length < processedData.length}
                    checked={processedData.length > 0 && selected.length === processedData.length}
                    onChange={handleSelectAllClick}
                    sx={{ color: 'primary.contrastText' }}
                  />
                </TableCell>
                <TableCell sx={{ color: 'primary.contrastText', fontWeight: 'bold' }}>
                  <TableSortLabel
                    active={orderBy === 'id'}
                    direction={orderBy === 'id' ? order : 'asc'}
                    onClick={() => handleRequestSort('id')}
                    sx={{ color: 'primary.contrastText !important' }}
                  >
                    ID
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ color: 'primary.contrastText', fontWeight: 'bold' }}>
                  <TableSortLabel
                    active={orderBy === 'timestamp'}
                    direction={orderBy === 'timestamp' ? order : 'asc'}
                    onClick={() => handleRequestSort('timestamp')}
                    sx={{ color: 'primary.contrastText !important' }}
                  >
                    Timestamp
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ color: 'primary.contrastText', fontWeight: 'bold' }}>
                  <TableSortLabel
                    active={orderBy === 'content_type'}
                    direction={orderBy === 'content_type' ? order : 'asc'}
                    onClick={() => handleRequestSort('content_type')}
                    sx={{ color: 'primary.contrastText !important' }}
                  >
                    Type
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ color: 'primary.contrastText', fontWeight: 'bold' }}>
                  Content Preview
                </TableCell>
                <TableCell sx={{ color: 'primary.contrastText', fontWeight: 'bold' }}>
                  <TableSortLabel
                    active={orderBy === 'size_bytes'}
                    direction={orderBy === 'size_bytes' ? order : 'asc'}
                    onClick={() => handleRequestSort('size_bytes')}
                    sx={{ color: 'primary.contrastText !important' }}
                  >
                    Size
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ color: 'primary.contrastText', fontWeight: 'bold' }}>
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {processedData
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((row) => {
                  const isItemSelected = isSelected(row.id)
                  const labelId = `enhanced-table-checkbox-${row.id}`

                  return (
                    <TableRow
                      hover
                      onClick={(event) => handleClick(event, row.id)}
                      role="checkbox"
                      aria-checked={isItemSelected}
                      tabIndex={-1}
                      key={row.id}
                      selected={isItemSelected}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell padding="checkbox">
                        <Checkbox
                          color="primary"
                          checked={isItemSelected}
                          inputProps={{ 'aria-labelledby': labelId }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={row.id}
                          size="small"
                          variant="outlined"
                          color="primary"
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {row.formatted_timestamp}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {row.age_minutes < 60
                              ? `${row.age_minutes}m ago`
                              : `${Math.round(row.age_minutes / 60)}h ago`
                            }
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={row.content_type}
                          size="small"
                          color={
                            row.content_type === 'URL' ? 'primary' :
                            row.content_type === 'Text' ? 'secondary' :
                            row.content_type === 'JSON' ? 'success' :
                            row.content_type === 'CSV' ? 'warning' :
                            row.content_type === 'Email' ? 'info' : 'default'
                          }
                          variant="filled"
                        />
                      </TableCell>
                      <TableCell sx={{ maxWidth: 300 }}>
                        <Box>
                          <Typography
                            variant="body2"
                            sx={{
                              fontFamily: 'monospace',
                              fontSize: '0.875rem',
                              lineHeight: 1.4,
                              wordBreak: 'break-word'
                            }}
                          >
                            {row.content_preview}
                          </Typography>
                          <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                            <Typography variant="caption" color="text.secondary">
                              {row.char_count} chars
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {row.word_count} words
                            </Typography>
                          </Stack>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {row.size_bytes < 1024 ? `${row.size_bytes} B` :
                           row.size_bytes < 1048576 ? `${(row.size_bytes / 1024).toFixed(1)} KB` :
                           `${(row.size_bytes / 1048576).toFixed(1)} MB`}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={0.5}>
                          <Tooltip title="Copy Content">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation()
                                navigator.clipboard.writeText(row.content)
                              }}
                            >
                              <ContentCopy fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="View Full Content">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation()
                                console.log('View full content:', row.content)
                              }}
                            >
                              <Visibility fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  )
                })}
              {emptyRows > 0 && (
                <TableRow style={{ height: (dense ? 33 : 53) * emptyRows }}>
                  <TableCell colSpan={7} />
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Enhanced Pagination */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 1 }}>
          <FormControlLabel
            control={<Switch checked={dense} onChange={(e) => setDense(e.target.checked)} />}
            label="Dense padding"
          />
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={processedData.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Box>
      </Paper>
    </Box>
  )
}

export default EnhancedDataTable
