import React, { useState, useEffect } from 'react'
import { Card, CardContent, Typography, Button, Box, Alert } from '@mui/material'

function SimpleTest() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)

  const testAPI = async () => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('Testing API...')
      const response = await fetch('http://localhost:3001/api/clipboard/history')
      console.log('Response status:', response.status)
      
      if (response.ok) {
        const result = await response.json()
        console.log('API data:', result)
        setData(result)
        setLastUpdate(new Date().toLocaleTimeString())
      } else {
        throw new Error(`API failed: ${response.status}`)
      }
    } catch (err) {
      console.error('API error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    testAPI()
  }, [])

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          🧪 Simple API Test
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>Status:</strong> {loading ? 'Loading...' : 'Ready'}<br/>
            <strong>Data Count:</strong> {data.length}<br/>
            <strong>Last Update:</strong> {lastUpdate || 'Never'}<br/>
            <strong>Error:</strong> {error || 'None'}
          </Typography>
        </Box>

        <Button
          variant="contained"
          onClick={testAPI}
          disabled={loading}
          sx={{ mr: 1 }}
        >
          Test API Now
        </Button>

        <Button
          variant="outlined"
          onClick={() => {
            // Test with hardcoded chart data
            const testData = [
              { label: 'Text', value: 34 },
              { label: 'JSON', value: 3 },
              { label: 'CSV', value: 12 },
              { label: 'URLs', value: 9 }
            ]
            console.log('Testing chart with hardcoded data:', testData)
            window.testChartData = testData
          }}
          sx={{ mr: 1 }}
        >
          Test Chart Data
        </Button>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {data.length > 0 && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Success!</strong> Found {data.length} clipboard entries.<br/>
              Latest entry: {data[0]?.content?.substring(0, 100)}...
            </Typography>
          </Alert>
        )}

        {data.length > 0 && (
          <Box sx={{ mt: 2, maxHeight: 200, overflow: 'auto' }}>
            <Typography variant="subtitle2" gutterBottom>
              Recent Entries:
            </Typography>
            {data.slice(0, 5).map((item, index) => (
              <Box key={item.id || index} sx={{ mb: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {new Date(item.timestamp).toLocaleString()}
                </Typography>
                <Typography variant="body2">
                  {item.content?.substring(0, 80)}...
                </Typography>
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default SimpleTest
