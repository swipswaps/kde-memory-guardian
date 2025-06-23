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
