import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import {
  AutoAwesome,
  TableChart,
  BarChart,
  PieChart,
  TrendingUp,
  Timeline,
  Cloud,
  Lightbulb,
} from '@mui/icons-material'

function SmartSuggestions({ data, onChartSelect, selectedChart }) {
  // Analyze data and provide smart suggestions
  const analyzeData = () => {
    if (!data || data.length === 0) {
      return {
        suggestions: [],
        insights: ['No data available for analysis']
      }
    }

    const suggestions = []
    const insights = []

    // Analyze data types and patterns
    let hasCSV = false
    let hasJSON = false
    let hasText = false
    let hasTimestamps = false
    let hasNumbers = false
    let totalEntries = data.length

    data.forEach(item => {
      const content = item.content || ''
      
      if (content.includes(',') && content.includes('\n')) {
        hasCSV = true
      }
      
      if (content.trim().startsWith('{') || content.trim().startsWith('[')) {
        hasJSON = true
      }
      
      if (content.length > 50 && !hasCSV && !hasJSON) {
        hasText = true
      }
      
      if (content.includes('start') && content.includes('end')) {
        hasTimestamps = true
      }
      
      if (/\d+/.test(content)) {
        hasNumbers = true
      }
    })

    // Generate suggestions based on analysis
    if (hasCSV) {
      suggestions.push({
        type: 'table',
        icon: <TableChart />,
        title: 'Start with Data Table',
        reason: 'Explore your CSV data structure first',
        confidence: 'High'
      })
      
      if (hasNumbers) {
        suggestions.push({
          type: 'bar',
          icon: <BarChart />,
          title: 'Bar Chart',
          reason: 'Perfect for comparing CSV categories',
          confidence: 'High'
        })
        
        suggestions.push({
          type: 'pie',
          icon: <PieChart />,
          title: 'Pie Chart',
          reason: 'Show proportions of your data',
          confidence: 'Medium'
        })
      }
    }

    if (hasJSON && hasTimestamps) {
      suggestions.push({
        type: 'gantt',
        icon: <Timeline />,
        title: 'Timeline Chart',
        reason: 'Your JSON contains timeline data',
        confidence: 'High'
      })
    }

    if (hasText) {
      suggestions.push({
        type: 'wordcloud',
        icon: <Cloud />,
        title: 'Word Cloud',
        reason: 'Visualize text frequency and themes',
        confidence: 'High'
      })
    }

    if (hasNumbers && data.length > 5) {
      suggestions.push({
        type: 'line',
        icon: <TrendingUp />,
        title: 'Line Chart',
        reason: 'Show trends in your numeric data',
        confidence: 'Medium'
      })
    }

    // Generate insights
    insights.push(`Found ${totalEntries} clipboard entries`)
    
    if (hasCSV) insights.push('✓ CSV data detected - great for charts')
    if (hasJSON) insights.push('✓ JSON data detected - structured format')
    if (hasText) insights.push('✓ Text content detected - good for word clouds')
    if (hasTimestamps) insights.push('✓ Timeline data detected - perfect for Gantt charts')
    if (hasNumbers) insights.push('✓ Numeric data detected - suitable for most chart types')

    // If no specific patterns, suggest starting with table
    if (suggestions.length === 0) {
      suggestions.push({
        type: 'table',
        icon: <TableChart />,
        title: 'Data Table',
        reason: 'Best starting point for any data',
        confidence: 'High'
      })
    }

    return { suggestions: suggestions.slice(0, 3), insights }
  }

  const { suggestions, insights } = analyzeData()

  if (suggestions.length === 0) {
    return (
      <Alert severity="info" sx={{ mb: 2 }}>
        Copy some data to your clipboard to see smart visualization suggestions!
      </Alert>
    )
  }

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AutoAwesome color="primary" />
          Smart Suggestions
        </Typography>

        {/* Insights */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom color="text.secondary">
            Data Analysis:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {insights.map((insight, index) => (
              <Chip 
                key={index}
                label={insight}
                size="small"
                variant="outlined"
                color={insight.includes('✓') ? 'success' : 'default'}
              />
            ))}
          </Box>
        </Box>

        {/* Suggestions */}
        <Typography variant="subtitle2" gutterBottom>
          Recommended Visualizations:
        </Typography>
        
        <List dense>
          {suggestions.map((suggestion, index) => (
            <ListItem 
              key={suggestion.type}
              sx={{ 
                border: selectedChart === suggestion.type ? '2px solid' : '1px solid',
                borderColor: selectedChart === suggestion.type ? 'primary.main' : 'divider',
                borderRadius: 1,
                mb: 1,
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'action.hover'
                }
              }}
              onClick={() => onChartSelect(suggestion.type)}
            >
              <ListItemIcon>
                {suggestion.icon}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2">
                      {suggestion.title}
                    </Typography>
                    <Chip 
                      label={suggestion.confidence}
                      size="small"
                      color={suggestion.confidence === 'High' ? 'success' : 'warning'}
                      variant="outlined"
                    />
                  </Box>
                }
                secondary={suggestion.reason}
              />
            </ListItem>
          ))}
        </List>

        {/* Quick action */}
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Button
            variant="outlined"
            startIcon={<Lightbulb />}
            onClick={() => onChartSelect('table')}
            size="small"
          >
            Start with Data Table
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}

export default SmartSuggestions
