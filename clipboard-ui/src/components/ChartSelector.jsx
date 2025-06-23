import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Box,
  Chip,
  Tooltip,
  Zoom,
} from '@mui/material'
import { styled } from '@mui/material/styles'

const ChartButton = styled(Button)(({ theme, selected, chartcolor }) => ({
  minHeight: 80,
  borderRadius: 12,
  border: `2px solid ${selected ? chartcolor : 'transparent'}`,
  backgroundColor: selected ? `${chartcolor}15` : theme.palette.background.paper,
  color: selected ? chartcolor : theme.palette.text.primary,
  transition: 'all 0.3s ease',
  '&:hover': {
    backgroundColor: `${chartcolor}20`,
    border: `2px solid ${chartcolor}`,
    transform: 'translateY(-2px)',
    boxShadow: `0 8px 25px ${chartcolor}30`,
  },
  display: 'flex',
  flexDirection: 'column',
  gap: 1,
}))

const ChartIcon = styled(Box)(({ chartcolor }) => ({
  fontSize: '2rem',
  color: chartcolor,
  marginBottom: '4px',
}))

function ChartSelector({ chartTypes, selectedChart, onChartChange }) {
  const getChartDescription = (chartId) => {
    // Use descriptions from chart types if available, otherwise fallback
    const chart = chartTypes.find(c => c.id === chartId)
    if (chart && chart.description) {
      return chart.description
    }

    const descriptions = {
      table: 'Explore raw data in spreadsheet format with sorting and filtering',
      bar: 'Perfect for comparing categories and showing discrete data values',
      pie: 'Ideal for showing parts of a whole, best with 3-8 categories',
      line: 'Great for showing trends over time or continuous data',
      wordcloud: 'Text frequency visualization with word importance sizing',
      gantt: 'Perfect for project timelines and task scheduling',
    }
    return descriptions[chartId] || 'Visualize your data in this format'
  }

  const getDataRequirements = (chartId) => {
    const requirements = {
      table: 'Any structured data',
      bar: 'Categories + Values',
      pie: '3-8 Categories + Values',
      line: 'Sequential Data Points',
      wordcloud: 'Text content',
      gantt: 'Tasks + Start/End Dates',
    }
    return requirements[chartId] || 'Any Data'
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          🎨 Chart Type Selector
          <Chip 
            label={`${chartTypes.length} types available`} 
            size="small" 
            color="primary" 
            variant="outlined"
          />
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Choose how to visualize your clipboard data. Start with the Data Table to explore your data structure.
        </Typography>

        <Grid container spacing={2}>
          {chartTypes.map((chart) => (
            <Grid item xs={6} sm={4} md={4} lg={2} key={chart.id}>
              <Tooltip
                title={
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      {chart.name}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.5, mb: 1 }}>
                      {getChartDescription(chart.id)}
                    </Typography>
                    <Chip 
                      label={getDataRequirements(chart.id)} 
                      size="small" 
                      sx={{ 
                        backgroundColor: `${chart.color}20`,
                        color: chart.color,
                        fontSize: '0.7rem'
                      }}
                    />
                  </Box>
                }
                arrow
                placement="top"
                TransitionComponent={Zoom}
              >
                <ChartButton
                  fullWidth
                  selected={selectedChart === chart.id}
                  chartcolor={chart.color}
                  onClick={() => onChartChange(chart.id)}
                  variant={selectedChart === chart.id ? 'contained' : 'outlined'}
                >
                  <ChartIcon chartcolor={chart.color}>
                    {chart.icon}
                  </ChartIcon>
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      fontWeight: selectedChart === chart.id ? 600 : 400,
                      fontSize: '0.75rem'
                    }}
                  >
                    {chart.name}
                  </Typography>
                </ChartButton>
              </Tooltip>
            </Grid>
          ))}
        </Grid>

        {/* Selected Chart Info */}
        {selectedChart && (
          <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
              📊 {chartTypes.find(c => c.id === selectedChart)?.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {getChartDescription(selectedChart)}
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Chip 
                label={`Requires: ${getDataRequirements(selectedChart)}`}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default ChartSelector
