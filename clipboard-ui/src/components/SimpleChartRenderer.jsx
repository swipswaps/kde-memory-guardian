import React from 'react'
import { Box, Typography, Paper, LinearProgress, Chip } from '@mui/material'
import DataTable from './DataTable'

function SimpleChartRenderer({ data, chartType, rawData }) {
  console.log('SimpleChartRenderer:', { chartType, data, rawData })

  // Handle table view
  if (chartType === 'table') {
    return <DataTable data={rawData || data} title="Clipboard Data Explorer" />
  }

  // Handle no data
  if (!data || data.length === 0) {
    return (
      <Box sx={{
        p: 4,
        textAlign: 'center',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <Typography variant="h4" sx={{ mb: 2, opacity: 0.5 }}>
          📊
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No data available for {chartType} chart
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
          Copy some structured data (CSV, JSON) or text to your clipboard to see beautiful visualizations
        </Typography>
        <Chip
          label="Try copying some data first"
          color="primary"
          variant="outlined"
          sx={{ fontWeight: 'bold' }}
        />
      </Box>
    )
  }

  // Simple Bar Chart using HTML/CSS
  if (chartType === 'bar') {
    const maxValue = Math.max(...data.map(d => d.value))

    return (
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, textAlign: 'center', color: 'primary.main' }}>
          📊 Content Type Distribution
        </Typography>

        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {data.map((item, index) => (
            <Paper key={index} elevation={2} sx={{ p: 2, borderRadius: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {item.label}
                </Typography>
                <Chip
                  label={`${item.value} entries`}
                  color="primary"
                  size="small"
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>
              <LinearProgress
                variant="determinate"
                value={(item.value / maxValue) * 100}
                sx={{
                  height: 12,
                  borderRadius: 2,
                  backgroundColor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: `hsl(${index * 80 + 200}, 70%, 50%)`,
                    borderRadius: 2,
                  }
                }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {((item.value / maxValue) * 100).toFixed(1)}% of total
              </Typography>
            </Paper>
          ))}
        </Box>
      </Box>
    )
  }

  // Simple Pie Chart using CSS
  if (chartType === 'pie') {
    const total = data.reduce((sum, item) => sum + item.value, 0)

    return (
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, textAlign: 'center', color: 'primary.main' }}>
          🥧 Content Distribution
        </Typography>

        {/* Visual pie representation using CSS circles */}
        <Box sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          mb: 3,
          minHeight: 200
        }}>
          <Box sx={{ position: 'relative', width: 160, height: 160 }}>
            {data.map((item, index) => {
              const percentage = (item.value / total) * 100
              const angle = (percentage / 100) * 360
              const rotation = data.slice(0, index).reduce((sum, prev) =>
                sum + ((prev.value / total) * 360), 0
              )

              return (
                <Box
                  key={index}
                  sx={{
                    position: 'absolute',
                    width: '100%',
                    height: '100%',
                    borderRadius: '50%',
                    background: `conic-gradient(from ${rotation}deg, hsl(${index * 80 + 200}, 70%, 50%) 0deg ${angle}deg, transparent ${angle}deg)`,
                    opacity: 0.8
                  }}
                />
              )
            })}
            <Box sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              backgroundColor: 'white',
              borderRadius: '50%',
              width: 80,
              height: 80,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 2
            }}>
              <Typography variant="h6" fontWeight="bold" color="primary">
                {total}
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Legend */}
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 1 }}>
          {data.map((item, index) => {
            const percentage = ((item.value / total) * 100).toFixed(1)
            return (
              <Paper key={index} elevation={1} sx={{ p: 1.5, borderRadius: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{
                    width: 16,
                    height: 16,
                    borderRadius: '50%',
                    backgroundColor: `hsl(${index * 80 + 200}, 70%, 50%)`
                  }} />
                  <Typography variant="body2" sx={{ flex: 1 }}>
                    {item.label}
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {percentage}%
                  </Typography>
                </Box>
              </Paper>
            )
          })}
        </Box>
      </Box>
    )
  }

  // Simple Line Chart
  if (chartType === 'line') {
    const maxValue = Math.max(...data.map(d => d.y))

    return (
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, textAlign: 'center', color: 'primary.main' }}>
          📈 Activity Timeline
        </Typography>

        <Paper elevation={2} sx={{ p: 3, borderRadius: 2, flex: 1 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
            {data.map((item, index) => (
              <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="body2" sx={{ minWidth: 120, fontWeight: 600 }}>
                  {item.label}
                </Typography>
                <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={(item.y / maxValue) * 100}
                    sx={{
                      flex: 1,
                      height: 8,
                      borderRadius: 1,
                      backgroundColor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: 'primary.main',
                        borderRadius: 1,
                      }
                    }}
                  />
                  <Chip
                    label={`${item.y}`}
                    size="small"
                    color="primary"
                    sx={{ minWidth: 50, fontWeight: 'bold' }}
                  />
                </Box>
              </Box>
            ))}
          </Box>
        </Paper>
      </Box>
    )
  }

  // Simple Word Cloud
  if (chartType === 'wordcloud') {
    return (
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, textAlign: 'center', color: 'primary.main' }}>
          ☁️ Word Frequency Analysis
        </Typography>

        <Paper elevation={2} sx={{ p: 3, borderRadius: 2, flex: 1, overflow: 'auto' }}>
          <Box sx={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 1.5,
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: 300
          }}>
            {data.slice(0, 40).map((word, index) => {
              const fontSize = Math.max(14, Math.min(32, word.size * 2))
              const opacity = Math.max(0.6, Math.min(1, word.size / 10))

              return (
                <Typography
                  key={index}
                  variant="body1"
                  sx={{
                    fontSize: `${fontSize}px`,
                    color: `hsl(${(index * 137.5) % 360}, 70%, 45%)`,
                    fontWeight: word.size > 5 ? 'bold' : 'normal',
                    opacity,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    padding: '4px 8px',
                    borderRadius: 1,
                    '&:hover': {
                      backgroundColor: 'primary.light',
                      color: 'white',
                      transform: 'scale(1.1)',
                      boxShadow: 2
                    }
                  }}
                  title={`"${word.text}" appears ${word.size} times`}
                >
                  {word.text}
                </Typography>
              )
            })}
          </Box>

          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, textAlign: 'center', display: 'block' }}>
            Showing top {Math.min(40, data.length)} words • Hover for frequency count
          </Typography>
        </Paper>
      </Box>
    )
  }

  // Simple Timeline/Gantt
  if (chartType === 'gantt' || chartType === 'timeline') {
    return (
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, textAlign: 'center', color: 'primary.main' }}>
          📅 Recent Clipboard Activity
        </Typography>

        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {data.slice(0, 15).map((item, index) => (
            <Paper
              key={index}
              elevation={2}
              sx={{
                p: 2.5,
                mb: 2,
                borderRadius: 2,
                borderLeft: `4px solid hsl(${index * 40}, 70%, 50%)`,
                transition: 'all 0.2s ease',
                '&:hover': {
                  transform: 'translateX(4px)',
                  boxShadow: 4
                }
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, flex: 1, mr: 2 }}>
                  {item.name}
                </Typography>
                <Chip
                  label={`#${index + 1}`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                📅 {new Date(item.start).toLocaleString()}
              </Typography>
              {item.progress !== undefined && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Progress: {(item.progress * 100).toFixed(0)}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={item.progress * 100}
                    sx={{
                      mt: 0.5,
                      height: 6,
                      borderRadius: 1,
                      backgroundColor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: `hsl(${index * 40}, 70%, 50%)`,
                        borderRadius: 1,
                      }
                    }}
                  />
                </Box>
              )}
            </Paper>
          ))}
        </Box>
      </Box>
    )
  }

  // Fallback
  return (
    <Box sx={{ p: 3, textAlign: 'center' }}>
      <Typography variant="h6" color="text.secondary">
        Chart type "{chartType}" not yet implemented
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        Available: bar, pie, line, wordcloud, timeline, table
      </Typography>
    </Box>
  )
}

export default SimpleChartRenderer
