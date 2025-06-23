import React, { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { Box, Typography, Alert } from '@mui/material'
import DataTable from './DataTable'

function ChartRenderer({ data, chartType, width = '100%', height = '400px', rawData }) {
  const svgRef = useRef()
  const containerRef = useRef()

  // Handle table view separately
  if (chartType === 'table') {
    console.log('ChartRenderer: Rendering table with rawData:', rawData, 'data:', data)
    return <DataTable data={rawData || data} title="Clipboard Data Explorer" />
  }

  useEffect(() => {
    console.log('ChartRenderer useEffect - chartType:', chartType, 'data:', data)

    if (!data || !svgRef.current) {
      console.log('ChartRenderer: No data or no SVG ref')
      return
    }

    // Clear previous chart
    d3.select(svgRef.current).selectAll('*').remove()

    // Get container dimensions
    const container = containerRef.current
    const containerWidth = container.offsetWidth
    const containerHeight = parseInt(height)

    console.log('ChartRenderer: Container dimensions:', containerWidth, 'x', containerHeight)

    try {
      switch (chartType) {
        case 'bar':
          renderBarChart(data, svgRef.current, containerWidth, containerHeight)
          break
        case 'pie':
          renderPieChart(data, svgRef.current, containerWidth, containerHeight)
          break
        case 'donut':
          renderDonutChart(data, svgRef.current, containerWidth, containerHeight)
          break
        case 'line':
          renderLineChart(data, svgRef.current, containerWidth, containerHeight)
          break
        case 'scatter':
          renderScatterPlot(data, svgRef.current, containerWidth, containerHeight)
          break
        case 'bubble':
          renderBubbleChart(data, svgRef.current, containerWidth, containerHeight)
          break
        case 'gantt':
          renderGanttChart(data, svgRef.current, containerWidth, containerHeight)
          break
        case 'treemap':
          renderTreemap(data, svgRef.current, containerWidth, containerHeight)
          break
        case 'heatmap':
          renderHeatmap(data, svgRef.current, containerWidth, containerHeight)
          break
        case 'wordcloud':
          renderWordCloud(data, svgRef.current, containerWidth, containerHeight)
          break
        default:
          renderBarChart(data, svgRef.current, containerWidth, containerHeight)
      }
    } catch (error) {
      console.error('Chart rendering error:', error)
    }
  }, [data, chartType, width, height])

  // Bar Chart Implementation
  const renderBarChart = (data, svg, width, height) => {
    console.log('Rendering bar chart with data:', data)

    if (!data || data.length === 0) {
      console.log('No data for bar chart')
      return
    }

    const margin = { top: 20, right: 30, bottom: 60, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const svgElement = d3.select(svg)
      .attr('width', width)
      .attr('height', height)

    const g = svgElement.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    const xScale = d3.scaleBand()
      .domain(data.map(d => d.label))
      .range([0, innerWidth])
      .padding(0.1)

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .range([innerHeight, 0])

    const colorScale = d3.scaleOrdinal(d3.schemeCategory10)

    // Bars
    g.selectAll('.bar')
      .data(data)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => xScale(d.label))
      .attr('width', xScale.bandwidth())
      .attr('y', innerHeight)
      .attr('height', 0)
      .attr('fill', (d, i) => colorScale(i))
      .attr('rx', 4)
      .transition()
      .duration(800)
      .attr('y', d => yScale(d.value))
      .attr('height', d => innerHeight - yScale(d.value))

    // X Axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale))
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)')

    // Y Axis
    g.append('g')
      .call(d3.axisLeft(yScale))

    // Value labels on bars
    g.selectAll('.label')
      .data(data)
      .enter().append('text')
      .attr('class', 'label')
      .attr('x', d => xScale(d.label) + xScale.bandwidth() / 2)
      .attr('y', d => yScale(d.value) - 5)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('fill', '#333')
      .text(d => d.value)
  }

  // Pie Chart Implementation
  const renderPieChart = (data, svg, width, height) => {
    const radius = Math.min(width, height) / 2 - 40

    const svgElement = d3.select(svg)
      .attr('width', width)
      .attr('height', height)

    const g = svgElement.append('g')
      .attr('transform', `translate(${width / 2},${height / 2})`)

    const colorScale = d3.scaleOrdinal(d3.schemeCategory10)

    const pie = d3.pie()
      .value(d => d.value)
      .sort(null)

    const arc = d3.arc()
      .innerRadius(0)
      .outerRadius(radius)

    const labelArc = d3.arc()
      .innerRadius(radius * 0.6)
      .outerRadius(radius * 0.6)

    const arcs = g.selectAll('.arc')
      .data(pie(data))
      .enter().append('g')
      .attr('class', 'arc')

    arcs.append('path')
      .attr('d', arc)
      .attr('fill', (d, i) => colorScale(i))
      .attr('stroke', 'white')
      .attr('stroke-width', 2)
      .transition()
      .duration(800)
      .attrTween('d', function(d) {
        const interpolate = d3.interpolate({ startAngle: 0, endAngle: 0 }, d)
        return function(t) {
          return arc(interpolate(t))
        }
      })

    arcs.append('text')
      .attr('transform', d => `translate(${labelArc.centroid(d)})`)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('fill', 'white')
      .style('font-weight', 'bold')
      .text(d => d.data.label)
  }

  // Donut Chart Implementation
  const renderDonutChart = (data, svg, width, height) => {
    const radius = Math.min(width, height) / 2 - 40

    const svgElement = d3.select(svg)
      .attr('width', width)
      .attr('height', height)

    const g = svgElement.append('g')
      .attr('transform', `translate(${width / 2},${height / 2})`)

    const colorScale = d3.scaleOrdinal(d3.schemeCategory10)

    const pie = d3.pie()
      .value(d => d.value)
      .sort(null)

    const arc = d3.arc()
      .innerRadius(radius * 0.4)
      .outerRadius(radius)

    const arcs = g.selectAll('.arc')
      .data(pie(data))
      .enter().append('g')
      .attr('class', 'arc')

    arcs.append('path')
      .attr('d', arc)
      .attr('fill', (d, i) => colorScale(i))
      .attr('stroke', 'white')
      .attr('stroke-width', 2)
      .transition()
      .duration(800)
      .attrTween('d', function(d) {
        const interpolate = d3.interpolate({ startAngle: 0, endAngle: 0 }, d)
        return function(t) {
          return arc(interpolate(t))
        }
      })

    // Center text
    g.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .style('font-size', '18px')
      .style('font-weight', 'bold')
      .text(`${data.length} items`)
  }

  // Line Chart Implementation
  const renderLineChart = (data, svg, width, height) => {
    const margin = { top: 20, right: 30, bottom: 40, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const svgElement = d3.select(svg)
      .attr('width', width)
      .attr('height', height)

    const g = svgElement.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    const xScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.x))
      .range([0, innerWidth])

    const yScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.y))
      .range([innerHeight, 0])

    const line = d3.line()
      .x(d => xScale(d.x))
      .y(d => yScale(d.y))
      .curve(d3.curveMonotoneX)

    // Line path
    const path = g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#1976d2')
      .attr('stroke-width', 3)
      .attr('d', line)

    // Animate line drawing
    const totalLength = path.node().getTotalLength()
    path
      .attr('stroke-dasharray', totalLength + ' ' + totalLength)
      .attr('stroke-dashoffset', totalLength)
      .transition()
      .duration(1500)
      .attr('stroke-dashoffset', 0)

    // Data points
    g.selectAll('.dot')
      .data(data)
      .enter().append('circle')
      .attr('class', 'dot')
      .attr('cx', d => xScale(d.x))
      .attr('cy', d => yScale(d.y))
      .attr('r', 0)
      .attr('fill', '#1976d2')
      .transition()
      .delay(1000)
      .duration(500)
      .attr('r', 4)

    // Axes
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale))

    g.append('g')
      .call(d3.axisLeft(yScale))
  }

  // Scatter Plot Implementation
  const renderScatterPlot = (data, svg, width, height) => {
    const margin = { top: 20, right: 30, bottom: 40, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const svgElement = d3.select(svg)
      .attr('width', width)
      .attr('height', height)

    const g = svgElement.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    const xScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.x))
      .range([0, innerWidth])

    const yScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.y))
      .range([innerHeight, 0])

    const colorScale = d3.scaleOrdinal(d3.schemeCategory10)

    // Scatter points
    g.selectAll('.dot')
      .data(data)
      .enter().append('circle')
      .attr('class', 'dot')
      .attr('cx', d => xScale(d.x))
      .attr('cy', d => yScale(d.y))
      .attr('r', 0)
      .attr('fill', (d, i) => colorScale(d.category || i))
      .attr('opacity', 0.7)
      .transition()
      .duration(800)
      .delay((d, i) => i * 50)
      .attr('r', 6)

    // Axes
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale))

    g.append('g')
      .call(d3.axisLeft(yScale))
  }



  if (!data) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Alert severity="info">
          No data available for visualization. Copy some data to your clipboard to get started!
        </Alert>
      </Box>
    )
  }

  return (
    <Box ref={containerRef} sx={{ width: '100%', height: '100%' }}>
      <svg ref={svgRef} style={{ width: '100%', height: '100%' }} />
    </Box>
  )
}

// Word Cloud Implementation
const renderWordCloud = (data, svg, width, height) => {
  const svgElement = d3.select(svg)
    .attr('width', width)
    .attr('height', height)

  const g = svgElement.append('g')
    .attr('transform', `translate(${width / 2},${height / 2})`)

  // Process text data for word frequency
  let words = []
  if (Array.isArray(data)) {
    // If data is already processed word frequency
    words = data.map(d => ({
      text: d.label || d.word || d.text,
      size: Math.max(12, Math.min(48, (d.value || 1) * 8))
    }))
  } else {
    // Extract words from raw text
    const allText = data.content || ''
    const wordCounts = {}
    const stopWords = new Set(['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'a', 'an'])

    allText.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 3 && !stopWords.has(word))
      .forEach(word => {
        wordCounts[word] = (wordCounts[word] || 0) + 1
      })

    words = Object.entries(wordCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 50)
      .map(([word, count]) => ({
        text: word,
        size: Math.max(12, Math.min(48, count * 8))
      }))
  }

  // Simple word cloud layout (spiral placement)
  const centerX = 0
  const centerY = 0
  let angle = 0
  let radius = 0

  words.forEach((word, i) => {
    const x = centerX + radius * Math.cos(angle)
    const y = centerY + radius * Math.sin(angle)

    g.append('text')
      .attr('x', x)
      .attr('y', y)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .style('font-size', `${word.size}px`)
      .style('font-family', 'Arial, sans-serif')
      .style('font-weight', 'bold')
      .style('fill', d3.schemeCategory10[i % 10])
      .style('opacity', 0)
      .text(word.text)
      .transition()
      .duration(1000)
      .delay(i * 100)
      .style('opacity', 0.8)

    // Update position for next word
    angle += 0.5
    radius += 2
    if (radius > Math.min(width, height) / 3) {
      radius = 0
      angle += 1
    }
  })
}

// Bubble Chart Implementation
const renderBubbleChart = (data, svg, width, height) => {
  const margin = { top: 20, right: 30, bottom: 40, left: 60 }
  const innerWidth = width - margin.left - margin.right
  const innerHeight = height - margin.top - margin.bottom

  const svgElement = d3.select(svg)
    .attr('width', width)
    .attr('height', height)

  const g = svgElement.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const xScale = d3.scaleLinear()
    .domain(d3.extent(data, d => d.x))
    .range([0, innerWidth])

  const yScale = d3.scaleLinear()
    .domain(d3.extent(data, d => d.y))
    .range([innerHeight, 0])

  const rScale = d3.scaleSqrt()
    .domain(d3.extent(data, d => d.r || d.value))
    .range([5, 30])

  const colorScale = d3.scaleOrdinal(d3.schemeCategory10)

  // Bubble circles
  g.selectAll('.bubble')
    .data(data)
    .enter().append('circle')
    .attr('class', 'bubble')
    .attr('cx', d => xScale(d.x))
    .attr('cy', d => yScale(d.y))
    .attr('r', 0)
    .attr('fill', (d, i) => colorScale(d.category || i))
    .attr('opacity', 0.7)
    .attr('stroke', 'white')
    .attr('stroke-width', 2)
    .transition()
    .duration(800)
    .delay((d, i) => i * 50)
    .attr('r', d => rScale(d.r || d.value))

  // Labels
  g.selectAll('.bubble-label')
    .data(data)
    .enter().append('text')
    .attr('class', 'bubble-label')
    .attr('x', d => xScale(d.x))
    .attr('y', d => yScale(d.y))
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .style('font-size', '10px')
    .style('fill', 'white')
    .style('font-weight', 'bold')
    .style('opacity', 0)
    .text(d => d.label)
    .transition()
    .delay(1000)
    .duration(500)
    .style('opacity', 1)

  // Axes
  g.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(xScale))

  g.append('g')
    .call(d3.axisLeft(yScale))
}

// Gantt Chart Implementation
const renderGanttChart = (data, svg, width, height) => {
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
    .attr('width', 0)
    .attr('height', yScale.bandwidth())
    .attr('fill', '#1976d2')
    .attr('opacity', 0.7)
    .attr('rx', 4)
    .transition()
    .duration(800)
    .attr('width', d => xScale(d.endDate) - xScale(d.startDate))

  // Progress bars
  g.selectAll('.progress')
    .data(tasks)
    .enter().append('rect')
    .attr('class', 'progress')
    .attr('x', d => xScale(d.startDate))
    .attr('y', d => yScale(d.name) + yScale.bandwidth() * 0.25)
    .attr('width', 0)
    .attr('height', yScale.bandwidth() * 0.5)
    .attr('fill', '#4caf50')
    .attr('rx', 2)
    .transition()
    .duration(800)
    .delay(400)
    .attr('width', d => (xScale(d.endDate) - xScale(d.startDate)) * (d.progress || 0))

  // Axes
  g.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(xScale))

  g.append('g')
    .call(d3.axisLeft(yScale))
}

// Treemap Implementation
const renderTreemap = (data, svg, width, height) => {
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
    .attr('width', 0)
    .attr('height', 0)
    .attr('fill', (d, i) => colorScale(i))
    .attr('opacity', 0.7)
    .attr('stroke', 'white')
    .attr('stroke-width', 2)
    .transition()
    .duration(800)
    .attr('width', d => d.x1 - d.x0)
    .attr('height', d => d.y1 - d.y0)

  leaf.append('text')
    .attr('x', 4)
    .attr('y', 14)
    .text(d => d.data.name)
    .attr('font-size', '12px')
    .attr('fill', 'white')
    .attr('font-weight', 'bold')
    .style('opacity', 0)
    .transition()
    .delay(800)
    .duration(400)
    .style('opacity', 1)
}

// Heatmap Implementation
const renderHeatmap = (data, svg, width, height) => {
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
    .attr('width', 0)
    .attr('height', 0)
    .attr('fill', d => colorScale(d.value))
    .attr('stroke', 'white')
    .attr('stroke-width', 1)
    .transition()
    .duration(800)
    .delay((d, i) => i * 20)
    .attr('width', xScale.bandwidth())
    .attr('height', yScale.bandwidth())

  // Axes
  g.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(xScale))

  g.append('g')
    .call(d3.axisLeft(yScale))
}

export default ChartRenderer
