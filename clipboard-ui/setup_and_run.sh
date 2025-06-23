#!/usr/bin/env bash
################################################################################
# setup_and_run.sh
# Setup and run the Material UI + D3.js Clipboard Visualizer
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}🎨 Material UI + D3.js Clipboard Visualizer Setup${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if Node.js is installed
if ! command -v node >/dev/null 2>&1; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm >/dev/null 2>&1; then
    echo -e "${RED}❌ npm is not installed${NC}"
    echo "Please install npm (usually comes with Node.js)"
    exit 1
fi

NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)

echo -e "${GREEN}✅ Node.js version: $NODE_VERSION${NC}"
echo -e "${GREEN}✅ npm version: $NPM_VERSION${NC}"
echo ""

echo -e "${YELLOW}📦 Step 1: Installing dependencies...${NC}"

# Install dependencies
if npm install; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    echo "Trying with --legacy-peer-deps flag..."
    npm install --legacy-peer-deps
fi

echo ""

echo -e "${YELLOW}🔧 Step 2: Setting up clipboard integration...${NC}"

# Create a simple backend API to interface with our clipboard manager
cat > clipboard_api.js << 'EOF'
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
EOF

echo -e "${GREEN}✅ Clipboard API created${NC}"
echo ""

echo -e "${YELLOW}📊 Step 3: Creating additional chart implementations...${NC}"

# Create extended chart implementations
mkdir -p src/charts
cat > src/charts/AdvancedCharts.js << 'EOF'
import * as d3 from 'd3'

export const renderGanttChart = (data, svg, width, height) => {
  const margin = { top: 20, right: 30, bottom: 40, left: 120 }
  const innerWidth = width - margin.left - margin.right
  const innerHeight = height - margin.top - margin.bottom

  const svgElement = d3.select(svg)
    .attr('width', width)
    .attr('height', height)

  const g = svgElement.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Parse dates
  const parseDate = d3.timeParse('%Y-%m-%d')
  const tasks = data.map(d => ({
    ...d,
    startDate: parseDate(d.start),
    endDate: parseDate(d.end)
  }))

  const xScale = d3.scaleTime()
    .domain(d3.extent(tasks.flatMap(d => [d.startDate, d.endDate])))
    .range([0, innerWidth])

  const yScale = d3.scaleBand()
    .domain(tasks.map(d => d.name))
    .range([0, innerHeight])
    .padding(0.1)

  // Task bars
  g.selectAll('.task')
    .data(tasks)
    .enter().append('rect')
    .attr('class', 'task')
    .attr('x', d => xScale(d.startDate))
    .attr('y', d => yScale(d.name))
    .attr('width', d => xScale(d.endDate) - xScale(d.startDate))
    .attr('height', yScale.bandwidth())
    .attr('fill', '#1976d2')
    .attr('opacity', 0.7)
    .attr('rx', 4)

  // Progress bars
  g.selectAll('.progress')
    .data(tasks)
    .enter().append('rect')
    .attr('class', 'progress')
    .attr('x', d => xScale(d.startDate))
    .attr('y', d => yScale(d.name) + yScale.bandwidth() * 0.25)
    .attr('width', d => (xScale(d.endDate) - xScale(d.startDate)) * d.progress)
    .attr('height', yScale.bandwidth() * 0.5)
    .attr('fill', '#4caf50')
    .attr('rx', 2)

  // Axes
  g.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(xScale))

  g.append('g')
    .call(d3.axisLeft(yScale))
}

export const renderTreemap = (data, svg, width, height) => {
  const svgElement = d3.select(svg)
    .attr('width', width)
    .attr('height', height)

  const root = d3.hierarchy(data)
    .sum(d => d.value)
    .sort((a, b) => b.value - a.value)

  d3.treemap()
    .size([width, height])
    .padding(2)
    (root)

  const colorScale = d3.scaleOrdinal(d3.schemeCategory10)

  const leaf = svgElement.selectAll('g')
    .data(root.leaves())
    .enter().append('g')
    .attr('transform', d => `translate(${d.x0},${d.y0})`)

  leaf.append('rect')
    .attr('width', d => d.x1 - d.x0)
    .attr('height', d => d.y1 - d.y0)
    .attr('fill', (d, i) => colorScale(i))
    .attr('opacity', 0.7)
    .attr('stroke', 'white')
    .attr('stroke-width', 2)

  leaf.append('text')
    .attr('x', 4)
    .attr('y', 14)
    .text(d => d.data.name)
    .attr('font-size', '12px')
    .attr('fill', 'white')
    .attr('font-weight', 'bold')
}

export const renderHeatmap = (data, svg, width, height) => {
  const margin = { top: 20, right: 30, bottom: 40, left: 60 }
  const innerWidth = width - margin.left - margin.right
  const innerHeight = height - margin.top - margin.bottom

  const svgElement = d3.select(svg)
    .attr('width', width)
    .attr('height', height)

  const g = svgElement.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const xValues = [...new Set(data.map(d => d.x))]
  const yValues = [...new Set(data.map(d => d.y))]

  const xScale = d3.scaleBand()
    .domain(xValues)
    .range([0, innerWidth])
    .padding(0.1)

  const yScale = d3.scaleBand()
    .domain(yValues)
    .range([0, innerHeight])
    .padding(0.1)

  const colorScale = d3.scaleSequential(d3.interpolateBlues)
    .domain(d3.extent(data, d => d.value))

  g.selectAll('.cell')
    .data(data)
    .enter().append('rect')
    .attr('class', 'cell')
    .attr('x', d => xScale(d.x))
    .attr('y', d => yScale(d.y))
    .attr('width', xScale.bandwidth())
    .attr('height', yScale.bandwidth())
    .attr('fill', d => colorScale(d.value))
    .attr('stroke', 'white')
    .attr('stroke-width', 1)

  // Axes
  g.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(xScale))

  g.append('g')
    .call(d3.axisLeft(yScale))
}
EOF

echo -e "${GREEN}✅ Advanced chart implementations created${NC}"
echo ""

echo -e "${YELLOW}🚀 Step 4: Starting the application...${NC}"

# Start the backend API in the background
echo "Starting clipboard API server..."
node clipboard_api.js &
API_PID=$!

# Wait a moment for the API to start
sleep 2

echo -e "${GREEN}✅ Clipboard API started (PID: $API_PID)${NC}"

# Start the React development server
echo "Starting React development server..."
echo ""
echo -e "${PURPLE}🎨 Your Material UI + D3.js Clipboard Visualizer will open at:${NC}"
echo -e "${BLUE}   http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}📋 Features available:${NC}"
echo "  • 🎯 9 different chart types (Bar, Pie, Line, Scatter, Bubble, Donut, Gantt, Treemap, Heatmap)"
echo "  • 📊 Real-time clipboard data integration"
echo "  • 🎨 Beautiful Material UI interface"
echo "  • 📱 Responsive design"
echo "  • 🔍 Data preview and analysis"
echo "  • 💾 Export capabilities"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop both servers${NC}"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping servers...${NC}"
    kill $API_PID 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Start the React app
npm run dev

# If we get here, cleanup
cleanup
