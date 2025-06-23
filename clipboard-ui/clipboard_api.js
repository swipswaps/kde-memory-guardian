const express = require('express')
const { exec } = require('child_process')
const cors = require('cors')
const path = require('path')

const app = express()
const PORT = 3001

app.use(cors())
app.use(express.json())

// Get clipboard history
app.get('/api/clipboard/history', (req, res) => {
  const limit = req.query.limit || 100
  
  exec(`clipboard_manager history --limit ${limit} --format json`, (error, stdout, stderr) => {
    if (error) {
      console.error('Error getting clipboard history:', error)
      // Return mock data if clipboard_manager is not available
      res.json(getMockData())
      return
    }
    
    try {
      const data = JSON.parse(stdout || '[]')
      res.json(data)
    } catch (parseError) {
      console.error('Error parsing clipboard data:', parseError)
      res.json(getMockData())
    }
  })
})

// Get current clipboard content
app.get('/api/clipboard/current', (req, res) => {
  exec('clipboard_manager get --format json', (error, stdout, stderr) => {
    if (error) {
      res.status(500).json({ error: 'Failed to get clipboard content' })
      return
    }
    
    try {
      const data = JSON.parse(stdout || '{}')
      res.json(data)
    } catch (parseError) {
      res.json({ content: stdout.trim(), content_type: 'Text' })
    }
  })
})

// Mock data for demonstration
function getMockData() {
  return [
    {
      id: '1',
      timestamp: new Date().toISOString(),
      content_type: 'Text',
      content: 'Product,Sales,Region\nLaptops,1500,North\nPhones,2300,South\nTablets,800,East\nDesktops,1200,West',
      size_bytes: 95
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      content_type: 'Text',
      content: '{"tasks": [{"name": "Design UI", "start": "2024-01-01", "end": "2024-01-15", "progress": 0.8}, {"name": "Backend API", "start": "2024-01-10", "end": "2024-01-25", "progress": 0.6}]}',
      size_bytes: 200
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      content_type: 'Text',
      content: 'Q1 Revenue: $125,000\nQ2 Revenue: $150,000\nQ3 Revenue: $175,000\nQ4 Revenue: $200,000',
      size_bytes: 85
    }
  ]
}

app.listen(PORT, () => {
  console.log(`🚀 Clipboard API server running on http://localhost:${PORT}`)
})
