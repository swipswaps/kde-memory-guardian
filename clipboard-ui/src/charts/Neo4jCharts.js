import * as d3 from 'd3'

/**
 * Neo4j-style Force-Directed Graph Visualization
 * Creates interactive network graphs similar to Neo4j Browser
 */
export const renderForceDirectedGraph = (data, svg, width, height, options = {}) => {
  const {
    nodeRadius = 20,
    linkDistance = 100,
    linkStrength = 0.5,
    chargeStrength = -300,
    nodeColors = d3.schemeCategory10,
    showLabels = true,
    enableZoom = true,
    enableDrag = true
  } = options

  // Clear previous content
  const svgElement = d3.select(svg)
    .attr('width', width)
    .attr('height', height)

  svgElement.selectAll('*').remove()

  // Create main group for zoom/pan
  const g = svgElement.append('g')

  // Setup zoom behavior
  if (enableZoom) {
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svgElement.call(zoom)
  }

  // Process data into nodes and links
  const nodes = data.nodes.map(d => ({ ...d, id: d.id }))
  const links = data.links.map(d => ({ ...d }))

  // Create color scale for node types
  const nodeTypeScale = d3.scaleOrdinal()
    .domain([...new Set(nodes.map(d => d.type || 'default'))])
    .range(nodeColors)

  // Create force simulation
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(linkDistance).strength(linkStrength))
    .force('charge', d3.forceManyBody().strength(chargeStrength))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(nodeRadius + 2))

  // Create links
  const link = g.append('g')
    .attr('class', 'links')
    .selectAll('line')
    .data(links)
    .enter().append('line')
    .attr('stroke', '#999')
    .attr('stroke-opacity', 0.6)
    .attr('stroke-width', d => Math.sqrt(d.weight || 1) * 2)

  // Create link labels
  const linkLabel = g.append('g')
    .attr('class', 'link-labels')
    .selectAll('text')
    .data(links)
    .enter().append('text')
    .attr('class', 'link-label')
    .attr('text-anchor', 'middle')
    .attr('font-size', '10px')
    .attr('fill', '#666')
    .attr('dy', -2)
    .text(d => d.relationship || d.label || '')

  // Create nodes
  const node = g.append('g')
    .attr('class', 'nodes')
    .selectAll('circle')
    .data(nodes)
    .enter().append('circle')
    .attr('r', d => d.size || nodeRadius)
    .attr('fill', d => nodeTypeScale(d.type || 'default'))
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .style('cursor', 'pointer')

  // Add node labels
  if (showLabels) {
    const nodeLabel = g.append('g')
      .attr('class', 'node-labels')
      .selectAll('text')
      .data(nodes)
      .enter().append('text')
      .attr('class', 'node-label')
      .attr('text-anchor', 'middle')
      .attr('dy', d => (d.size || nodeRadius) + 15)
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('fill', '#333')
      .text(d => d.label || d.name || d.id)

    // Update label positions
    simulation.on('tick', () => {
      nodeLabel
        .attr('x', d => d.x)
        .attr('y', d => d.y)
    })
  }

  // Add drag behavior
  if (enableDrag) {
    const drag = d3.drag()
      .on('start', (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart()
        d.fx = d.x
        d.fy = d.y
      })
      .on('drag', (event, d) => {
        d.fx = event.x
        d.fy = event.y
      })
      .on('end', (event, d) => {
        if (!event.active) simulation.alphaTarget(0)
        d.fx = null
        d.fy = null
      })

    node.call(drag)
  }

  // Add hover effects
  node
    .on('mouseover', function(event, d) {
      d3.select(this)
        .transition()
        .duration(200)
        .attr('r', (d.size || nodeRadius) * 1.2)
        .attr('stroke-width', 4)

      // Highlight connected links
      link
        .attr('stroke-opacity', l => 
          (l.source.id === d.id || l.target.id === d.id) ? 1 : 0.1
        )
        .attr('stroke-width', l => 
          (l.source.id === d.id || l.target.id === d.id) ? 
          Math.sqrt(l.weight || 1) * 3 : Math.sqrt(l.weight || 1) * 2
        )
    })
    .on('mouseout', function(event, d) {
      d3.select(this)
        .transition()
        .duration(200)
        .attr('r', d.size || nodeRadius)
        .attr('stroke-width', 2)

      // Reset link styles
      link
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.sqrt(d.weight || 1) * 2)
    })

  // Add click events for node expansion
  node.on('click', (event, d) => {
    console.log('Node clicked:', d)
    // Emit custom event for node interaction
    const customEvent = new CustomEvent('nodeClick', { detail: d })
    svg.dispatchEvent(customEvent)
  })

  // Update positions on simulation tick
  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)

    linkLabel
      .attr('x', d => (d.source.x + d.target.x) / 2)
      .attr('y', d => (d.source.y + d.target.y) / 2)

    node
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
  })

  return { simulation, nodes, links }
}

/**
 * Neo4j-style Hierarchical Graph
 * Creates tree-like structures with Neo4j styling
 */
export const renderHierarchicalGraph = (data, svg, width, height, options = {}) => {
  const {
    nodeRadius = 15,
    levelHeight = 80,
    nodeColors = d3.schemeCategory10,
    showLabels = true
  } = options

  const svgElement = d3.select(svg)
    .attr('width', width)
    .attr('height', height)

  svgElement.selectAll('*').remove()

  const g = svgElement.append('g')
    .attr('transform', `translate(40, 40)`)

  // Create hierarchy
  const root = d3.hierarchy(data)
  const treeLayout = d3.tree()
    .size([width - 80, height - 80])

  treeLayout(root)

  // Create color scale
  const colorScale = d3.scaleOrdinal()
    .domain([...new Set(root.descendants().map(d => d.data.type || 'default'))])
    .range(nodeColors)

  // Create links
  const links = g.selectAll('.link')
    .data(root.links())
    .enter().append('path')
    .attr('class', 'link')
    .attr('d', d3.linkHorizontal()
      .x(d => d.y)
      .y(d => d.x))
    .attr('fill', 'none')
    .attr('stroke', '#999')
    .attr('stroke-width', 2)
    .attr('stroke-opacity', 0.6)

  // Create nodes
  const nodes = g.selectAll('.node')
    .data(root.descendants())
    .enter().append('g')
    .attr('class', 'node')
    .attr('transform', d => `translate(${d.y},${d.x})`)

  nodes.append('circle')
    .attr('r', d => d.data.size || nodeRadius)
    .attr('fill', d => colorScale(d.data.type || 'default'))
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .style('cursor', 'pointer')

  // Add labels
  if (showLabels) {
    nodes.append('text')
      .attr('dy', '0.31em')
      .attr('x', d => d.children ? -6 : 6)
      .attr('text-anchor', d => d.children ? 'end' : 'start')
      .text(d => d.data.name || d.data.label || d.data.id)
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('fill', '#333')
  }

  return { root, nodes, links }
}

/**
 * Neo4j-style Circular Network
 * Creates circular layouts similar to Neo4j's circular arrangement
 */
export const renderCircularNetwork = (data, svg, width, height, options = {}) => {
  const {
    innerRadius = 50,
    outerRadius = Math.min(width, height) / 2 - 50,
    nodeRadius = 12,
    nodeColors = d3.schemeCategory10
  } = options

  const svgElement = d3.select(svg)
    .attr('width', width)
    .attr('height', height)

  svgElement.selectAll('*').remove()

  const g = svgElement.append('g')
    .attr('transform', `translate(${width / 2}, ${height / 2})`)

  const nodes = data.nodes
  const links = data.links

  // Position nodes in a circle
  const angleStep = (2 * Math.PI) / nodes.length
  nodes.forEach((node, i) => {
    const angle = i * angleStep
    const radius = innerRadius + (outerRadius - innerRadius) * (node.level || 0.5)
    node.x = Math.cos(angle) * radius
    node.y = Math.sin(angle) * radius
  })

  // Create color scale
  const colorScale = d3.scaleOrdinal()
    .domain([...new Set(nodes.map(d => d.type || 'default'))])
    .range(nodeColors)

  // Create links
  const link = g.append('g')
    .selectAll('path')
    .data(links)
    .enter().append('path')
    .attr('d', d => {
      const source = nodes.find(n => n.id === d.source)
      const target = nodes.find(n => n.id === d.target)
      return `M${source.x},${source.y} Q0,0 ${target.x},${target.y}`
    })
    .attr('fill', 'none')
    .attr('stroke', '#999')
    .attr('stroke-width', 2)
    .attr('stroke-opacity', 0.6)

  // Create nodes
  const node = g.append('g')
    .selectAll('circle')
    .data(nodes)
    .enter().append('circle')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', nodeRadius)
    .attr('fill', d => colorScale(d.type || 'default'))
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .style('cursor', 'pointer')

  // Add labels
  const labels = g.append('g')
    .selectAll('text')
    .data(nodes)
    .enter().append('text')
    .attr('x', d => d.x)
    .attr('y', d => d.y + nodeRadius + 15)
    .attr('text-anchor', 'middle')
    .attr('font-size', '10px')
    .attr('font-weight', 'bold')
    .attr('fill', '#333')
    .text(d => d.label || d.name || d.id)

  return { nodes, links, node, link, labels }
}
