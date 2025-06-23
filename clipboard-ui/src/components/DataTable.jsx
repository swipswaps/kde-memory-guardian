import React, { useState, useMemo } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  TextField,
  Box,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Button,
  Menu,
  MenuItem,
} from '@mui/material'
import {
  Search,
  Download,
  FilterList,
  Sort,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material'

function DataTable({ data, title = "Data Table" }) {
  console.log('DataTable received data:', data)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(25)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortColumn, setSortColumn] = useState(null)
  const [sortDirection, setSortDirection] = useState('asc')
  const [hiddenColumns, setHiddenColumns] = useState(new Set())
  const [anchorEl, setAnchorEl] = useState(null)

  // Process and flatten data for table display
  const processedData = useMemo(() => {
    if (!data || data.length === 0) return { rows: [], columns: [] }

    // Try to extract tabular data from clipboard entries
    let allRows = []
    let allColumns = new Set()

    data.forEach((item, itemIndex) => {
      const content = item.content || ''
      
      // Try to parse as CSV
      if (content.includes(',') && content.includes('\n')) {
        const lines = content.trim().split('\n')
        if (lines.length > 1) {
          const headers = lines[0].split(',').map(h => h.trim())
          headers.forEach(h => allColumns.add(h))
          
          for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim())
            const row = { _source: `Entry ${itemIndex + 1}`, _timestamp: item.timestamp }
            headers.forEach((header, index) => {
              row[header] = values[index] || ''
            })
            allRows.push(row)
          }
          return
        }
      }

      // Try to parse as JSON
      if (content.trim().startsWith('{') || content.trim().startsWith('[')) {
        try {
          const jsonData = JSON.parse(content)
          if (Array.isArray(jsonData)) {
            jsonData.forEach((obj, objIndex) => {
              if (typeof obj === 'object') {
                Object.keys(obj).forEach(key => allColumns.add(key))
                allRows.push({
                  ...obj,
                  _source: `Entry ${itemIndex + 1}.${objIndex + 1}`,
                  _timestamp: item.timestamp
                })
              }
            })
          } else if (typeof jsonData === 'object') {
            Object.keys(jsonData).forEach(key => allColumns.add(key))
            allRows.push({
              ...jsonData,
              _source: `Entry ${itemIndex + 1}`,
              _timestamp: item.timestamp
            })
          }
          return
        } catch (e) {
          // Not valid JSON, continue
        }
      }

      // Parse key-value pairs
      if (content.includes(':')) {
        const lines = content.split('\n').filter(line => line.includes(':'))
        if (lines.length > 0) {
          const row = { _source: `Entry ${itemIndex + 1}`, _timestamp: item.timestamp }
          lines.forEach(line => {
            const [key, ...valueParts] = line.split(':')
            const value = valueParts.join(':').trim()
            const cleanKey = key.trim()
            allColumns.add(cleanKey)
            row[cleanKey] = value
          })
          allRows.push(row)
          return
        }
      }

      // Fallback: treat as single text entry
      allColumns.add('Content')
      allRows.push({
        Content: content,
        _source: `Entry ${itemIndex + 1}`,
        _timestamp: item.timestamp
      })
    })

    // Add metadata columns
    allColumns.add('_source')
    allColumns.add('_timestamp')

    const columns = Array.from(allColumns)
    return { rows: allRows, columns }
  }, [data])

  // Filter and sort data
  const filteredAndSortedData = useMemo(() => {
    let filtered = processedData.rows

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(row =>
        Object.values(row).some(value =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    }

    // Apply sorting
    if (sortColumn) {
      filtered = [...filtered].sort((a, b) => {
        const aVal = a[sortColumn] || ''
        const bVal = b[sortColumn] || ''
        
        // Try numeric comparison first
        const aNum = parseFloat(aVal)
        const bNum = parseFloat(bVal)
        if (!isNaN(aNum) && !isNaN(bNum)) {
          return sortDirection === 'asc' ? aNum - bNum : bNum - aNum
        }
        
        // String comparison
        const comparison = String(aVal).localeCompare(String(bVal))
        return sortDirection === 'asc' ? comparison : -comparison
      })
    }

    return filtered
  }, [processedData.rows, searchTerm, sortColumn, sortDirection])

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
  }

  const toggleColumnVisibility = (column) => {
    const newHidden = new Set(hiddenColumns)
    if (newHidden.has(column)) {
      newHidden.delete(column)
    } else {
      newHidden.add(column)
    }
    setHiddenColumns(newHidden)
  }

  const exportToCSV = () => {
    const visibleColumns = processedData.columns.filter(col => !hiddenColumns.has(col))
    const csvContent = [
      visibleColumns.join(','),
      ...filteredAndSortedData.map(row =>
        visibleColumns.map(col => `"${String(row[col] || '').replace(/"/g, '""')}"`).join(',')
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'clipboard_data.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  const visibleColumns = processedData.columns.filter(col => !hiddenColumns.has(col))
  const paginatedData = filteredAndSortedData.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )

  if (!data || data.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No data available
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Copy some structured data (CSV, JSON) to your clipboard to see it here
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Debug: data = {JSON.stringify(data)}
        </Typography>
      </Box>
    )
  }

  // Simple working table view
  if (data.length > 0) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          {title} - {data.length} entries found
        </Typography>

        <TableContainer component={Paper} sx={{ maxHeight: 400, mt: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Content Type</TableCell>
                <TableCell>Content Preview</TableCell>
                <TableCell>Size</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.slice(0, 10).map((item, index) => (
                <TableRow key={item.id || index}>
                  <TableCell>
                    {new Date(item.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Chip label={item.content_type} size="small" />
                  </TableCell>
                  <TableCell>
                    {String(item.content).substring(0, 100)}
                    {item.content.length > 100 ? '...' : ''}
                  </TableCell>
                  <TableCell>
                    {item.size_bytes} bytes
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {data.length > 10 && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Showing first 10 of {data.length} entries
          </Typography>
        )}
      </Box>
    )
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header with controls */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          {title}
        </Typography>
        
        <Chip 
          label={`${filteredAndSortedData.length} rows`} 
          color="primary" 
          variant="outlined" 
        />
        
        <TextField
          size="small"
          placeholder="Search data..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
          }}
          sx={{ minWidth: 200 }}
        />
        
        <Button
          startIcon={<FilterList />}
          onClick={(e) => setAnchorEl(e.currentTarget)}
          variant="outlined"
          size="small"
        >
          Columns
        </Button>
        
        <Button
          startIcon={<Download />}
          onClick={exportToCSV}
          variant="outlined"
          size="small"
        >
          Export CSV
        </Button>
      </Box>

      {/* Column visibility menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        {processedData.columns.map(column => (
          <MenuItem key={column} onClick={() => toggleColumnVisibility(column)}>
            <IconButton size="small" sx={{ mr: 1 }}>
              {hiddenColumns.has(column) ? <VisibilityOff /> : <Visibility />}
            </IconButton>
            {column}
          </MenuItem>
        ))}
      </Menu>

      {/* Data table */}
      <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              {visibleColumns.map(column => (
                <TableCell 
                  key={column}
                  sx={{ 
                    fontWeight: 'bold',
                    backgroundColor: 'grey.50',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                  onClick={() => handleSort(column)}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    {column}
                    {sortColumn === column && (
                      <Sort 
                        sx={{ 
                          fontSize: 16,
                          transform: sortDirection === 'desc' ? 'rotate(180deg)' : 'none'
                        }} 
                      />
                    )}
                  </Box>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedData.map((row, index) => (
              <TableRow key={index} hover>
                {visibleColumns.map(column => (
                  <TableCell key={column}>
                    {column === '_timestamp' && row[column] ? 
                      new Date(row[column]).toLocaleString() :
                      String(row[column] || '')
                    }
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <TablePagination
        component="div"
        count={filteredAndSortedData.length}
        page={page}
        onPageChange={(e, newPage) => setPage(newPage)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => {
          setRowsPerPage(parseInt(e.target.value, 10))
          setPage(0)
        }}
        rowsPerPageOptions={[10, 25, 50, 100]}
      />
    </Box>
  )
}

export default DataTable
