import React, { useState } from 'react'
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Collapse,
  Box,
  Tooltip,
  Divider,
  Button,
} from '@mui/material'
import {
  ContentCopy,
  ExpandMore,
  ExpandLess,
  Refresh,
  DataObject,
  TextFields,
  Link,
  Numbers,
  Schedule,
} from '@mui/icons-material'
import { formatDistanceToNow } from 'date-fns'

function DataPreview({ data, onRefresh }) {
  const [expandedItems, setExpandedItems] = useState(new Set())

  const toggleExpanded = (id) => {
    const newExpanded = new Set(expandedItems)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedItems(newExpanded)
  }

  const getContentTypeIcon = (content) => {
    if (content.trim().startsWith('{') || content.trim().startsWith('[')) {
      return <DataObject color="success" />
    }
    if (content.includes('http')) {
      return <Link color="primary" />
    }
    if (content.includes(',') && content.includes('\n')) {
      return <Numbers color="warning" />
    }
    return <TextFields color="action" />
  }

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

  const getContentPreview = (content, maxLength = 100) => {
    if (content.length <= maxLength) return content
    return content.substring(0, maxLength) + '...'
  }

  const copyToClipboard = async (content) => {
    try {
      await navigator.clipboard.writeText(content)
      // Could add a toast notification here
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
    }
  }

  const getVisualizationSuggestion = (content) => {
    const type = getContentTypeLabel(content)
    const suggestions = {
      JSON: 'Try Pie Chart or Tree Map',
      CSV: 'Perfect for Bar Chart or Line Chart',
      URL: 'Great for Pie Chart (domain analysis)',
      Text: 'Word Cloud or Bar Chart (word frequency)'
    }
    return suggestions[type] || 'Multiple chart types available'
  }

  return (
    <Card sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6">📋 Clipboard Data</Typography>
            <Chip 
              label={`${data.length} entries`} 
              size="small" 
              color="primary" 
              variant="outlined"
            />
          </Box>
        }
        action={
          <Tooltip title="Refresh clipboard data">
            <IconButton onClick={onRefresh} size="small">
              <Refresh />
            </IconButton>
          </Tooltip>
        }
        sx={{ pb: 1 }}
      />
      
      <CardContent sx={{ flex: 1, overflow: 'auto', pt: 0 }}>
        {data.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No clipboard data available
            </Typography>
            <Button 
              variant="outlined" 
              onClick={onRefresh} 
              sx={{ mt: 2 }}
              startIcon={<Refresh />}
            >
              Load Data
            </Button>
          </Box>
        ) : (
          <List dense>
            {data.map((item, index) => {
              const isExpanded = expandedItems.has(item.id)
              const contentType = getContentTypeLabel(item.content)
              const timeAgo = item.timestamp 
                ? formatDistanceToNow(new Date(item.timestamp), { addSuffix: true })
                : 'Unknown time'

              return (
                <React.Fragment key={item.id || index}>
                  <ListItem
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      mb: 1,
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <ListItemIcon>
                      {getContentTypeIcon(item.content)}
                    </ListItemIcon>
                    
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Chip 
                            label={contentType} 
                            size="small" 
                            color={
                              contentType === 'JSON' ? 'success' :
                              contentType === 'CSV' ? 'warning' :
                              contentType === 'URL' ? 'primary' : 'default'
                            }
                            variant="outlined"
                          />
                          <Typography variant="caption" color="text.secondary">
                            {item.size_bytes} bytes
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              fontFamily: 'monospace',
                              fontSize: '0.8rem',
                              mb: 0.5,
                              wordBreak: 'break-word'
                            }}
                          >
                            {getContentPreview(item.content)}
                          </Typography>
                          
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                            <Schedule sx={{ fontSize: 14 }} />
                            <Typography variant="caption" color="text.secondary">
                              {timeAgo}
                            </Typography>
                          </Box>
                          
                          <Typography 
                            variant="caption" 
                            color="primary.main"
                            sx={{ 
                              display: 'block',
                              mt: 0.5,
                              fontStyle: 'italic'
                            }}
                          >
                            💡 {getVisualizationSuggestion(item.content)}
                          </Typography>
                        </Box>
                      }
                    />
                    
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                      <Tooltip title="Copy to clipboard">
                        <IconButton 
                          size="small" 
                          onClick={() => copyToClipboard(item.content)}
                        >
                          <ContentCopy fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title={isExpanded ? "Collapse" : "Expand"}>
                        <IconButton 
                          size="small" 
                          onClick={() => toggleExpanded(item.id)}
                        >
                          {isExpanded ? <ExpandLess /> : <ExpandMore />}
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItem>
                  
                  <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                    <Box sx={{ ml: 4, mr: 2, mb: 2, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Full Content:
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontFamily: 'monospace',
                          fontSize: '0.8rem',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          maxHeight: 200,
                          overflow: 'auto',
                          backgroundColor: 'white',
                          p: 1,
                          borderRadius: 1,
                          border: '1px solid',
                          borderColor: 'divider'
                        }}
                      >
                        {item.content}
                      </Typography>
                      
                      {item.timestamp && (
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                          Timestamp: {new Date(item.timestamp).toLocaleString()}
                        </Typography>
                      )}
                    </Box>
                  </Collapse>
                  
                  {index < data.length - 1 && <Divider sx={{ my: 1 }} />}
                </React.Fragment>
              )
            })}
          </List>
        )}
      </CardContent>
    </Card>
  )
}

export default DataPreview
