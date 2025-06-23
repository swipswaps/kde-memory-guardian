import React, { useMemo } from 'react'
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip, 
  Paper,
  Grid,
  LinearProgress,
  Alert
} from '@mui/material'
import { 
  TrendingUp, 
  Psychology, 
  DataUsage, 
  Schedule,
  Language,
  Code
} from '@mui/icons-material'

function SmartInsights({ data }) {
  const insights = useMemo(() => {
    if (!data || data.length === 0) return null

    const now = new Date()
    const oneHour = 60 * 60 * 1000
    const oneDay = 24 * oneHour

    // Time-based analysis
    const recentEntries = data.filter(item => 
      new Date(item.timestamp) > new Date(now - oneHour)
    ).length

    const todayEntries = data.filter(item => 
      new Date(item.timestamp) > new Date(now - oneDay)
    ).length

    // Content analysis
    const avgContentLength = Math.round(
      data.reduce((sum, item) => sum + (item.content?.length || 0), 0) / data.length
    )

    const contentTypes = {
      code: data.filter(item => 
        item.content?.includes('function') || 
        item.content?.includes('const ') ||
        item.content?.includes('import ') ||
        item.content?.includes('class ')
      ).length,
      urls: data.filter(item => 
        item.content?.includes('http')
      ).length,
      json: data.filter(item => 
        item.content?.trim().startsWith('{')
      ).length,
      csv: data.filter(item => 
        item.content?.includes(',') && item.content?.includes('\n')
      ).length
    }

    // Pattern detection
    const duplicates = data.filter((item, index, arr) => 
      arr.findIndex(other => other.content === item.content) !== index
    ).length

    const longContent = data.filter(item => 
      (item.content?.length || 0) > 1000
    ).length

    // Activity patterns
    const hourlyActivity = {}
    data.forEach(item => {
      const hour = new Date(item.timestamp).getHours()
      hourlyActivity[hour] = (hourlyActivity[hour] || 0) + 1
    })

    const peakHour = Object.entries(hourlyActivity)
      .sort(([,a], [,b]) => b - a)[0]

    return {
      activity: {
        recent: recentEntries,
        today: todayEntries,
        peakHour: peakHour ? `${peakHour[0]}:00` : 'N/A',
        peakCount: peakHour ? peakHour[1] : 0
      },
      content: {
        avgLength: avgContentLength,
        types: contentTypes,
        duplicates,
        longContent
      },
      recommendations: generateRecommendations(data, contentTypes, recentEntries)
    }
  }, [data])

  if (!insights) return null

  return (
    <Card elevation={3} sx={{ borderRadius: 3 }}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main', mb: 3 }}>
          🧠 Smart Insights
        </Typography>

        <Grid container spacing={3}>
          {/* Activity Insights */}
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 2, borderRadius: 2, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Schedule color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Activity Patterns
                </Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Recent Activity (Last Hour)
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="h4" color="primary.main" fontWeight="bold">
                    {insights.activity.recent}
                  </Typography>
                  <Typography variant="body2">entries</Typography>
                </Box>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Peak Activity Hour
                </Typography>
                <Typography variant="h6" fontWeight="bold">
                  {insights.activity.peakHour} ({insights.activity.peakCount} entries)
                </Typography>
              </Box>

              <LinearProgress
                variant="determinate"
                value={(insights.activity.today / data.length) * 100}
                sx={{ height: 8, borderRadius: 1 }}
              />
              <Typography variant="caption" color="text.secondary">
                {insights.activity.today} of {data.length} entries today
              </Typography>
            </Paper>
          </Grid>

          {/* Content Insights */}
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 2, borderRadius: 2, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <DataUsage color="secondary" />
                <Typography variant="h6" fontWeight="bold">
                  Content Analysis
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                <Chip 
                  icon={<Code />} 
                  label={`${insights.content.types.code} Code`} 
                  color="info" 
                  size="small"
                />
                <Chip 
                  icon={<Language />} 
                  label={`${insights.content.types.urls} URLs`} 
                  color="success" 
                  size="small"
                />
                <Chip 
                  label={`${insights.content.types.json} JSON`} 
                  color="warning" 
                  size="small"
                />
                <Chip 
                  label={`${insights.content.types.csv} CSV`} 
                  color="error" 
                  size="small"
                />
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Average Content Length: <strong>{insights.content.avgLength} chars</strong>
              </Typography>
              
              {insights.content.duplicates > 0 && (
                <Typography variant="body2" color="warning.main">
                  ⚠️ {insights.content.duplicates} duplicate entries detected
                </Typography>
              )}
            </Paper>
          </Grid>

          {/* Smart Recommendations */}
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 2, borderRadius: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Psychology color="success" />
                <Typography variant="h6" fontWeight="bold">
                  AI Recommendations
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {insights.recommendations.map((rec, index) => (
                  <Alert 
                    key={index} 
                    severity={rec.type} 
                    variant="outlined"
                    sx={{ borderRadius: 2 }}
                  >
                    <Typography variant="body2">
                      <strong>{rec.title}:</strong> {rec.message}
                    </Typography>
                  </Alert>
                ))}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}

function generateRecommendations(data, contentTypes, recentActivity) {
  const recommendations = []

  // Chart recommendations based on content
  if (contentTypes.csv > 0) {
    recommendations.push({
      type: 'success',
      title: 'Perfect for Bar Charts',
      message: `You have ${contentTypes.csv} CSV entries - ideal for bar and pie chart visualizations`
    })
  }

  if (contentTypes.json > 0) {
    recommendations.push({
      type: 'info',
      title: 'Timeline Ready',
      message: `${contentTypes.json} JSON entries detected - great for timeline and Gantt charts`
    })
  }

  if (contentTypes.code > 0) {
    recommendations.push({
      type: 'warning',
      title: 'Code Analysis',
      message: `${contentTypes.code} code snippets found - consider using word cloud for keyword analysis`
    })
  }

  // Activity recommendations
  if (recentActivity > 5) {
    recommendations.push({
      type: 'success',
      title: 'High Activity',
      message: 'You\'re actively copying data - perfect time for real-time analysis!'
    })
  } else if (recentActivity === 0) {
    recommendations.push({
      type: 'info',
      title: 'Ready for Analysis',
      message: 'Copy some new data to see live updates and fresh insights'
    })
  }

  // Data quality recommendations
  const duplicateRatio = data.filter((item, index, arr) => 
    arr.findIndex(other => other.content === item.content) !== index
  ).length / data.length

  if (duplicateRatio > 0.2) {
    recommendations.push({
      type: 'warning',
      title: 'Duplicate Content',
      message: 'Consider cleaning up duplicate entries for better analysis accuracy'
    })
  }

  return recommendations
}

export default SmartInsights
