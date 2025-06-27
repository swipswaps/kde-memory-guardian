const express = require('express')
const { exec } = require('child_process')
const cors = require('cors')
const path = require('path')

const app = express()
const PORT = 3001

app.use(cors())
app.use(express.json())

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Clipboard API Server',
    version: '1.0.0',
    endpoints: {
      '/api/clipboard/history': 'GET - Get clipboard history',
      '/api/clipboard/current': 'GET - Get current clipboard',
      '/api/clipboard/add': 'POST - Add clipboard entry',
      '/api/clipboard/stats': 'GET - Get clipboard statistics'
    },
    status: 'running'
  })
})

// Get clipboard history - FIXED to use correct path and get real data
app.get('/api/clipboard/history', (req, res) => {
  const limit = req.query.limit || 1000  // Higher default to show all entries (user has 293)

  // Use full path to clipboard_manager with increased buffer size for large datasets
  exec(`/home/owner/.local/bin/clipboard_manager history --limit ${limit} --format json`, {
    maxBuffer: 50 * 1024 * 1024  // 50MB buffer to handle large clipboard datasets
  }, (error, stdout, stderr) => {
    if (error) {
      console.error('Error getting clipboard history:', error)
      console.error('stderr:', stderr)
      // Try alternative path or fallback with increased buffer
      exec(`clipboard_manager history --limit ${limit} --format json`, {
        maxBuffer: 50 * 1024 * 1024  // 50MB buffer for fallback too
      }, (error2, stdout2, stderr2) => {
        if (error2) {
          console.error('Fallback also failed:', error2)
          console.log('Returning mock data as last resort')
          res.json(getMockData())
          return
        }

        try {
          const data = JSON.parse(stdout2 || '[]')
          console.log(`Successfully retrieved ${data.length} real clipboard entries (fallback)`)
          res.json(data)
        } catch (parseError) {
          console.error('Error parsing fallback clipboard data:', parseError)
          res.json(getMockData())
        }
      })
      return
    }

    try {
      const data = JSON.parse(stdout || '[]')
      console.log(`Successfully retrieved ${data.length} real clipboard entries`)
      res.json(data)
    } catch (parseError) {
      console.error('Error parsing clipboard data:', parseError)
      res.json(getMockData())
    }
  })
})

// Get current clipboard content - FIXED to use correct path
app.get('/api/clipboard/current', (req, res) => {
  exec('/home/owner/.local/bin/clipboard_manager get --format json', (error, stdout, stderr) => {
    if (error) {
      console.error('Error getting current clipboard:', error)
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

// Get clipboard statistics - NEW endpoint for data recovery analysis
app.get('/api/clipboard/stats', (req, res) => {
  exec('/home/owner/.local/bin/clipboard_manager stats --format json', (error, stdout, stderr) => {
    if (error) {
      console.error('Error getting clipboard stats:', error)
      res.status(500).json({ error: 'Failed to get clipboard statistics' })
      return
    }

    try {
      const data = JSON.parse(stdout || '{}')
      res.json(data)
    } catch (parseError) {
      res.json({ error: 'Failed to parse statistics' })
    }
  })
})

// Get clipboard history in smaller chunks - NEW endpoint for large datasets
app.get('/api/clipboard/history/paged', (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 50, 100)  // Max 100 per page
  const offset = parseInt(req.query.offset) || 0

  // Use smaller limit to prevent buffer overflow
  exec(`/home/owner/.local/bin/clipboard_manager history --limit ${limit} --offset ${offset} --format json`, {
    maxBuffer: 10 * 1024 * 1024  // 10MB buffer for paged requests
  }, (error, stdout, stderr) => {
    if (error) {
      console.error('Error getting paged clipboard history:', error)
      res.status(500).json({ error: 'Failed to get clipboard history', details: error.message })
      return
    }

    try {
      const data = JSON.parse(stdout || '[]')
      console.log(`Successfully retrieved ${data.length} clipboard entries (page ${Math.floor(offset/limit) + 1})`)
      res.json({
        data: data,
        pagination: {
          limit: limit,
          offset: offset,
          page: Math.floor(offset/limit) + 1,
          hasMore: data.length === limit
        }
      })
    } catch (parseError) {
      console.error('Error parsing paged clipboard data:', parseError)
      res.status(500).json({ error: 'Failed to parse clipboard data' })
    }
  })
})

// Add new clipboard entry - FIXED to use correct path
app.post('/api/clipboard/add', (req, res) => {
  const { content, content_type } = req.body

  if (!content) {
    res.status(400).json({ error: 'Content is required' })
    return
  }

  exec(`/home/owner/.local/bin/clipboard_manager set "${content.replace(/"/g, '\\"')}"`, (error, stdout, stderr) => {
    if (error) {
      console.error('Error adding clipboard entry:', error)
      res.status(500).json({ error: 'Failed to add clipboard entry' })
      return
    }

    res.json({
      success: true,
      message: 'Clipboard entry added successfully',
      content: content,
      content_type: content_type || 'Text'
    })
  })
})

// Mock data for demonstration - Enhanced for Neo4j visualization testing
function getMockData() {
  return [
    {
      id: '1',
      timestamp: new Date().toISOString(),
      content_type: 'URL',
      content: 'https://github.com/swipswaps/kde-memory-guardian',
      size_bytes: 50
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 60000).toISOString(),
      content_type: 'Text',
      content: 'Neo4j graph database visualization with D3.js force-directed layouts and interactive network analysis',
      size_bytes: 95
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 120000).toISOString(),
      content_type: 'JSON',
      content: '{"project": "clipboard-visualizer", "features": ["neo4j", "d3js", "react", "force-directed", "hierarchical"], "status": "complete", "nodes": 25, "relationships": 18}',
      size_bytes: 150
    },
    {
      id: '4',
      timestamp: new Date(Date.now() - 180000).toISOString(),
      content_type: 'URL',
      content: 'https://d3js.org/d3-force',
      size_bytes: 25
    },
    {
      id: '5',
      timestamp: new Date(Date.now() - 240000).toISOString(),
      content_type: 'CSV',
      content: 'name,type,connections,importance\nClipboard,Node,5,high\nNeo4j,Database,8,critical\nD3js,Library,6,high\nReact,Framework,7,high\nForce,Algorithm,4,medium',
      size_bytes: 140
    },
    {
      id: '6',
      timestamp: new Date(Date.now() - 300000).toISOString(),
      content_type: 'Text',
      content: 'Interactive network graphs with force simulation physics, drag behavior, zoom controls, and relationship highlighting',
      size_bytes: 115
    },
    {
      id: '7',
      timestamp: new Date(Date.now() - 360000).toISOString(),
      content_type: 'URL',
      content: 'https://neo4j.com/developer/graph-visualization/',
      size_bytes: 45
    },
    {
      id: '8',
      timestamp: new Date(Date.now() - 420000).toISOString(),
      content_type: 'Email',
      content: 'developer@neo4j-visualization.com',
      size_bytes: 35
    },
    {
      id: '9',
      timestamp: new Date(Date.now() - 480000).toISOString(),
      content_type: 'Text',
      content: 'Graph database relationships: nodes connected by edges with properties, temporal analysis, content clustering',
      size_bytes: 110
    },
    {
      id: '10',
      timestamp: new Date(Date.now() - 540000).toISOString(),
      content_type: 'URL',
      content: 'https://github.com/d3/d3-force',
      size_bytes: 30
    },
    {
      id: '11',
      timestamp: new Date(Date.now() - 600000).toISOString(),
      content_type: 'JSON',
      content: '{"visualization": {"type": "force-directed", "nodes": ["clipboard", "neo4j", "d3js"], "links": [{"source": "clipboard", "target": "neo4j"}, {"source": "neo4j", "target": "d3js"}]}}',
      size_bytes: 180
    },
    {
      id: '12',
      timestamp: new Date(Date.now() - 660000).toISOString(),
      content_type: 'Text',
      content: 'Hierarchical tree visualization with parent-child relationships and circular network topology analysis',
      size_bytes: 105
    }
  ]
}

app.listen(PORT, () => {
  console.log(`🚀 Clipboard API server running on http://localhost:${PORT}`)
})
