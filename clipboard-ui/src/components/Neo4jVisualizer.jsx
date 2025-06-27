import React, { useRef, useEffect, useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Slider,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  ButtonGroup,
  Tooltip,
  IconButton,
  Stack,
  Divider,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Fab,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Badge
} from '@mui/material'
import {
  AccountTree,
  Hub,
  RadioButtonUnchecked,
  Refresh,
  ZoomIn,
  ZoomOut,
  CenterFocusStrong,
  ExpandMore,
  Settings,
  Tune,
  Palette,
  Speed,
  Timeline,
  Fullscreen,
  FullscreenExit,
  Save,
  Share,
  Download,
  Visibility,
  VisibilityOff,
  PlayArrow,
  Pause,
  Stop,
  SkipNext,
  SkipPrevious,
  Menu,
  Close
} from '@mui/icons-material'
import {
  renderForceDirectedGraph,
  renderHierarchicalGraph,
  renderCircularNetwork
} from '../charts/Neo4jCharts'

const VISUALIZATION_TYPES = [
  {
    id: 'force',
    name: 'Force-Directed Network',
    icon: <Hub />,
    description: 'Interactive network with physics simulation',
    color: '#1976d2',
    features: ['Physics Simulation', 'Drag & Drop', 'Auto Layout', 'Clustering']
  },
  {
    id: 'hierarchical',
    name: 'Hierarchical Tree',
    icon: <AccountTree />,
    description: 'Tree structure with parent-child relationships',
    color: '#388e3c',
    features: ['Tree Layout', 'Parent-Child', 'Expandable', 'Structured']
  },
  {
    id: 'circular',
    name: 'Circular Network',
    icon: <RadioButtonUnchecked />,
    description: 'Nodes arranged in circular patterns',
    color: '#f57c00',
    features: ['Radial Layout', 'Curved Links', 'Topology', 'Symmetrical']
  }
]

const PRESET_CONFIGURATIONS = [
  {
    name: 'Exploration',
    description: 'Best for discovering relationships',
    settings: { nodeRadius: 25, linkDistance: 150, chargeStrength: -400 }
  },
  {
    name: 'Compact',
    description: 'Dense layout for many nodes',
    settings: { nodeRadius: 15, linkDistance: 80, chargeStrength: -200 }
  },
  {
    name: 'Spacious',
    description: 'Spread out for detailed analysis',
    settings: { nodeRadius: 30, linkDistance: 200, chargeStrength: -600 }
  },
  {
    name: 'Performance',
    description: 'Optimized for large datasets',
    settings: { nodeRadius: 12, linkDistance: 60, chargeStrength: -150 }
  }
]

function Neo4jVisualizer({ data, width = 800, height = 600 }) {
  const svgRef = useRef()
  const [visualizationType, setVisualizationType] = useState('force')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [graphData, setGraphData] = useState(null)
  const [simulation, setSimulation] = useState(null)
  const [graphControls, setGraphControls] = useState(null)

  // Enhanced UI state
  const [controlsOpen, setControlsOpen] = useState(false)
  const [fullscreen, setFullscreen] = useState(false)
  const [isPlaying, setIsPlaying] = useState(true)
  const [selectedPreset, setSelectedPreset] = useState('Exploration')

  // Visualization options
  const [showLabels, setShowLabels] = useState(true)
  const [enableZoom, setEnableZoom] = useState(true)
  const [enableDrag, setEnableDrag] = useState(true)
  const [nodeRadius, setNodeRadius] = useState(25)
  const [linkDistance, setLinkDistance] = useState(150)
  const [chargeStrength, setChargeStrength] = useState(-400)
  const [animationSpeed, setAnimationSpeed] = useState(1)
  const [showStats, setShowStats] = useState(true)
  const [colorScheme, setColorScheme] = useState('default')

  // Process clipboard data into graph format
  useEffect(() => {
    if (data && data.length > 0) {
      processDataToGraph(data)
    }
  }, [data])

  // Re-render when visualization type or options change
  useEffect(() => {
    if (graphData) {
      renderVisualization()
    }
  }, [graphData, visualizationType, showLabels, enableZoom, enableDrag, nodeRadius, linkDistance, chargeStrength])

  const processDataToGraph = (clipboardData) => {
    setLoading(true)
    try {
      // Create nodes and links from clipboard data
      const nodes = []
      const links = []
      const nodeMap = new Map()

      // Process different types of clipboard content
      clipboardData.forEach((item, index) => {
        const nodeId = `item_${index}`
        const contentType = getContentType(item.content)
        
        // Create main content node
        const node = {
          id: nodeId,
          label: item.content.substring(0, 30) + (item.content.length > 30 ? '...' : ''),
          type: contentType,
          size: Math.min(30, Math.max(10, item.content.length / 10)),
          timestamp: item.timestamp,
          fullContent: item.content
        }
        
        nodes.push(node)
        nodeMap.set(nodeId, node)

        // Create type category nodes
        const typeNodeId = `type_${contentType}`
        if (!nodeMap.has(typeNodeId)) {
          const typeNode = {
            id: typeNodeId,
            label: contentType,
            type: 'category',
            size: 25,
            isCategory: true
          }
          nodes.push(typeNode)
          nodeMap.set(typeNodeId, typeNode)
        }

        // Link content to type
        links.push({
          source: nodeId,
          target: typeNodeId,
          relationship: 'IS_TYPE',
          weight: 1
        })

        // Create temporal links (items close in time)
        if (index > 0) {
          const prevItem = clipboardData[index - 1]
          const timeDiff = new Date(item.timestamp) - new Date(prevItem.timestamp)
          if (timeDiff < 300000) { // 5 minutes
            links.push({
              source: `item_${index - 1}`,
              target: nodeId,
              relationship: 'FOLLOWS',
              weight: Math.max(0.1, 1 - (timeDiff / 300000))
            })
          }
        }

        // Create similarity links for similar content
        if (contentType === 'URL') {
          const domain = extractDomain(item.content)
          const domainNodeId = `domain_${domain}`
          
          if (!nodeMap.has(domainNodeId)) {
            const domainNode = {
              id: domainNodeId,
              label: domain,
              type: 'domain',
              size: 20,
              isDomain: true
            }
            nodes.push(domainNode)
            nodeMap.set(domainNodeId, domainNode)
          }

          links.push({
            source: nodeId,
            target: domainNodeId,
            relationship: 'FROM_DOMAIN',
            weight: 1
          })
        }
      })

      // Add word frequency nodes for text content
      const textItems = clipboardData.filter(item => getContentType(item.content) === 'Text')
      if (textItems.length > 0) {
        const wordFreq = getWordFrequency(textItems.map(item => item.content).join(' '))
        const topWords = Object.entries(wordFreq)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 10)

        topWords.forEach(([word, freq]) => {
          const wordNodeId = `word_${word}`
          const wordNode = {
            id: wordNodeId,
            label: word,
            type: 'keyword',
            size: Math.min(25, 10 + freq * 2),
            frequency: freq,
            isKeyword: true
          }
          nodes.push(wordNode)

          // Link to text items containing this word
          textItems.forEach((item, index) => {
            if (item.content.toLowerCase().includes(word.toLowerCase())) {
              links.push({
                source: `item_${clipboardData.indexOf(item)}`,
                target: wordNodeId,
                relationship: 'CONTAINS',
                weight: freq / 10
              })
            }
          })
        })
      }

      setGraphData({ nodes, links })
      setError(null)
    } catch (err) {
      setError('Failed to process data: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const renderVisualization = () => {
    if (!graphData || !svgRef.current) return

    const options = {
      nodeRadius,
      linkDistance,
      chargeStrength,
      showLabels,
      enableZoom,
      enableDrag,
      nodeColors: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    }

    try {
      let result
      switch (visualizationType) {
        case 'force':
          result = renderForceDirectedGraph(graphData, svgRef.current, width, height, options)
          setSimulation(result.simulation)
          setGraphControls(result) // Store all control functions
          break
        case 'hierarchical':
          // Convert graph data to hierarchical format
          const hierarchicalData = convertToHierarchical(graphData)
          result = renderHierarchicalGraph(hierarchicalData, svgRef.current, width, height, options)
          setGraphControls(result)
          break
        case 'circular':
          result = renderCircularNetwork(graphData, svgRef.current, width, height, options)
          setGraphControls(result)
          break
        default:
          throw new Error(`Unknown visualization type: ${visualizationType}`)
      }
    } catch (err) {
      setError('Visualization error: ' + err.message)
    }
  }

  const convertToHierarchical = (graphData) => {
    try {
      if (!graphData || !graphData.nodes || !Array.isArray(graphData.nodes)) {
        console.warn('Invalid graph data for hierarchical conversion:', graphData)
        return { name: 'Root', children: [] }
      }

      // Find category nodes as root level
      const categoryNodes = graphData.nodes.filter(n => n.isCategory)
      const contentNodes = graphData.nodes.filter(n => !n.isCategory && !n.isDomain && !n.isKeyword)
      const links = graphData.links || []

      if (categoryNodes.length === 0) {
        // No categories, create a simple flat hierarchy
        return {
          name: 'Clipboard Data',
          children: contentNodes.map(n => ({
            ...n,
            name: n.label || n.id || 'Unknown',
            type: n.type || 'content'
          }))
        }
      }

      // Create hierarchical structure with categories
      const root = {
        name: 'Clipboard Data',
        type: 'root',
        children: categoryNodes.map(cat => {
          const categoryChildren = contentNodes.filter(node => {
            return links.some(link => {
              const sourceId = typeof link.source === 'object' ? link.source.id : link.source
              const targetId = typeof link.target === 'object' ? link.target.id : link.target
              return sourceId === node.id && targetId === cat.id && link.relationship === 'IS_TYPE'
            })
          })

          return {
            ...cat,
            name: cat.label || cat.id || 'Category',
            type: cat.type || 'category',
            children: categoryChildren.map(n => ({
              ...n,
              name: n.label || n.id || 'Item',
              type: n.type || 'content'
            }))
          }
        })
      }

      // Add orphaned nodes (nodes without category relationships)
      const orphanedNodes = contentNodes.filter(node => {
        return !links.some(link => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source
          return sourceId === node.id && link.relationship === 'IS_TYPE'
        })
      })

      if (orphanedNodes.length > 0) {
        root.children.push({
          id: 'orphaned',
          name: 'Other Items',
          type: 'category',
          children: orphanedNodes.map(n => ({
            ...n,
            name: n.label || n.id || 'Item',
            type: n.type || 'content'
          }))
        })
      }

      return root
    } catch (error) {
      console.error('Error converting to hierarchical data:', error)
      return { name: 'Root', children: [] }
    }
  }

  const getContentType = (content) => {
    if (content.trim().startsWith('{') || content.trim().startsWith('[')) return 'JSON'
    if (content.includes('http://') || content.includes('https://')) return 'URL'
    if (content.includes(',') && content.includes('\n')) return 'CSV'
    if (content.includes('@') && content.includes('.')) return 'Email'
    return 'Text'
  }

  const extractDomain = (url) => {
    try {
      return new URL(url).hostname
    } catch {
      return 'unknown'
    }
  }

  const getWordFrequency = (text) => {
    const words = text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 3)
    
    const freq = {}
    words.forEach(word => {
      freq[word] = (freq[word] || 0) + 1
    })
    
    return freq
  }

  // Enhanced control functions
  const handleRefresh = () => {
    if (data) {
      processDataToGraph(data)
    }
  }

  const handleCenterView = () => {
    if (graphControls && graphControls.centerGraph) {
      graphControls.centerGraph()
    } else if (simulation) {
      simulation.alpha(0.3).restart()
    }
  }

  const handlePresetChange = (presetName) => {
    const preset = PRESET_CONFIGURATIONS.find(p => p.name === presetName)
    if (preset) {
      setSelectedPreset(presetName)
      setNodeRadius(preset.settings.nodeRadius)
      setLinkDistance(preset.settings.linkDistance)
      setChargeStrength(preset.settings.chargeStrength)
    }
  }

  const handlePlayPause = () => {
    if (simulation) {
      if (isPlaying) {
        simulation.stop()
        setIsPlaying(false)
      } else {
        simulation.alpha(0.3).restart()
        setIsPlaying(true)
      }
    }
  }

  const handleExport = (format) => {
    if (!svgRef.current) return

    const svg = svgRef.current
    const serializer = new XMLSerializer()
    const svgString = serializer.serializeToString(svg)

    if (format === 'svg') {
      const blob = new Blob([svgString], { type: 'image/svg+xml' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'network-graph.svg'
      a.click()
    } else if (format === 'png') {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      const img = new Image()
      img.onload = () => {
        canvas.width = img.width
        canvas.height = img.height
        ctx.drawImage(img, 0, 0)
        canvas.toBlob((blob) => {
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = 'network-graph.png'
          a.click()
        })
      }
      img.src = 'data:image/svg+xml;base64,' + btoa(svgString)
    }
  }

  const toggleFullscreen = () => {
    setFullscreen(!fullscreen)
  }

  const handleShowLabelsToggle = (show) => {
    setShowLabels(show)
    if (graphControls && graphControls.toggleLabels) {
      graphControls.toggleLabels(show)
    }
  }

  const handleParameterUpdate = () => {
    if (graphControls && graphControls.updateParameters) {
      graphControls.updateParameters({
        nodeRadius,
        linkDistance,
        chargeStrength,
        showLabels
      })
    }
  }

  // Update parameters when they change
  useEffect(() => {
    if (graphControls && graphControls.updateParameters) {
      const timeoutId = setTimeout(() => {
        handleParameterUpdate()
      }, 300) // Debounce parameter updates

      return () => clearTimeout(timeoutId)
    }
  }, [nodeRadius, linkDistance, chargeStrength])

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Processing graph data...</Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    )
  }

  if (!data || data.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', p: 4 }}>
        <Typography variant="h6" color="text.secondary">
          No clipboard data available for network visualization
        </Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 2 }}>
      {/* Controls */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Visualization Type</InputLabel>
            <Select
              value={visualizationType}
              onChange={(e) => setVisualizationType(e.target.value)}
              label="Visualization Type"
            >
              {VISUALIZATION_TYPES.map(type => (
                <MenuItem key={type.id} value={type.id}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {type.icon}
                    {type.name}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <FormControlLabel
              control={<Switch checked={showLabels} onChange={(e) => handleShowLabelsToggle(e.target.checked)} />}
              label="Show Labels"
            />
            <FormControlLabel
              control={<Switch checked={enableZoom} onChange={(e) => setEnableZoom(e.target.checked)} />}
              label="Enable Zoom"
            />
            <FormControlLabel
              control={<Switch checked={enableDrag} onChange={(e) => setEnableDrag(e.target.checked)} />}
              label="Enable Drag"
            />
            <Button startIcon={<Refresh />} onClick={handleRefresh} size="small">
              Refresh
            </Button>
            <Button startIcon={<CenterFocusStrong />} onClick={handleCenterView} size="small">
              Center
            </Button>
          </Box>
        </Grid>
      </Grid>

      {/* Visualization Parameters */}
      {visualizationType === 'force' && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Force Simulation Parameters</Typography>
            <Grid container spacing={3}>
              <Grid item xs={4}>
                <Typography gutterBottom>Node Radius: {nodeRadius}</Typography>
                <Slider
                  value={nodeRadius}
                  onChange={(e, value) => setNodeRadius(value)}
                  min={5}
                  max={50}
                  step={1}
                />
              </Grid>
              <Grid item xs={4}>
                <Typography gutterBottom>Link Distance: {linkDistance}</Typography>
                <Slider
                  value={linkDistance}
                  onChange={(e, value) => setLinkDistance(value)}
                  min={50}
                  max={300}
                  step={10}
                />
              </Grid>
              <Grid item xs={4}>
                <Typography gutterBottom>Charge Strength: {chargeStrength}</Typography>
                <Slider
                  value={chargeStrength}
                  onChange={(e, value) => setChargeStrength(value)}
                  min={-1000}
                  max={-50}
                  step={50}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Graph Statistics */}
      {graphData && (
        <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip label={`${graphData.nodes.length} nodes`} color="primary" variant="outlined" />
          <Chip label={`${graphData.links.length} relationships`} color="secondary" variant="outlined" />
          <Chip 
            label={`${graphData.nodes.filter(n => n.isCategory).length} categories`} 
            color="success" 
            variant="outlined" 
          />
          <Chip 
            label={`${graphData.nodes.filter(n => n.isKeyword).length} keywords`} 
            color="warning" 
            variant="outlined" 
          />
        </Box>
      )}

      {/* Main Visualization */}
      <Paper elevation={3} sx={{ p: 2, borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          {VISUALIZATION_TYPES.find(t => t.id === visualizationType)?.name} - Clipboard Network
        </Typography>
        <Box sx={{ border: '1px solid #ddd', borderRadius: 1, overflow: 'hidden' }}>
          <svg
            ref={svgRef}
            width={width}
            height={height}
            style={{
              display: 'block',
              background: '#fafafa',
              maxWidth: '100%',
              height: 'auto'
            }}
          />
        </Box>
      </Paper>
    </Box>
  )
}

export default Neo4jVisualizer
