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

  // Add node labels (always create but control visibility)
  const nodeLabel = g.append('g')
    .attr('class', 'node-labels')
    .selectAll('text')
    .data(nodes)
    .enter().append('text')
    .attr('class', 'node-label')
    .attr('text-anchor', 'middle')
    .attr('dy', '0.35em')
    .attr('font-size', '11px')
    .attr('font-weight', 'bold')
    .attr('fill', '#333')
    .attr('pointer-events', 'none')
    .style('display', showLabels ? 'block' : 'none')
    .text(d => {
      const text = d.label || d.name || d.id || ''
      return text.length > 15 ? text.substring(0, 12) + '...' : text
    })

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

    nodeLabel
      .attr('x', d => d.x)
      .attr('y', d => d.y)
  })

  // Helper functions for external control
  const toggleLabels = (show) => {
    nodeLabel.style('display', show ? 'block' : 'none')
  }

  const centerGraph = () => {
    // Reset node positions and restart simulation
    nodes.forEach(node => {
      node.fx = null
      node.fy = null
    })
    simulation.alpha(0.5).restart()

    // Center the view using zoom transform
    const svgElement = d3.select(svg)
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svgElement.call(zoom)
    svgElement.transition()
      .duration(750)
      .call(zoom.transform, d3.zoomIdentity.translate(0, 0).scale(1))
  }

  const updateParameters = (newOptions) => {
    const {
      nodeRadius: newNodeRadius = nodeRadius,
      linkDistance: newLinkDistance = linkDistance,
      chargeStrength: newChargeStrength = chargeStrength,
      showLabels: newShowLabels = showLabels
    } = newOptions

    // Update forces
    simulation
      .force('link').distance(newLinkDistance)
      .force('charge').strength(newChargeStrength)
      .force('collision').radius(newNodeRadius + 2)

    // Update node sizes
    node.attr('r', newNodeRadius)

    // Update label visibility
    toggleLabels(newShowLabels)

    // Restart simulation with new parameters
    simulation.alpha(0.3).restart()
  }

  return {
    simulation,
    nodes,
    links,
    toggleLabels,
    centerGraph,
    updateParameters,
    nodeLabel,
    node,
    link
  }
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

  // Setup zoom behavior
  const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      g.attr('transform', `translate(40, 40) ${event.transform}`)
    })

  svgElement.call(zoom)

  const g = svgElement.append('g')
    .attr('transform', `translate(40, 40)`)

  // Validate and process data
  if (!data || typeof data !== 'object') {
    console.error('Invalid hierarchical data:', data)
    return {
      root: null,
      nodes: null,
      links: null,
      toggleLabels: () => {},
      centerGraph: () => {},
      updateParameters: () => {}
    }
  }

  // Create hierarchy
  let root
  try {
    root = d3.hierarchy(data)
    const treeLayout = d3.tree()
      .size([height - 80, width - 160]) // Swap for horizontal layout

    treeLayout(root)
  } catch (error) {
    console.error('Error creating hierarchy:', error)
    return {
      root: null,
      nodes: null,
      links: null,
      toggleLabels: () => {},
      centerGraph: () => {},
      updateParameters: () => {}
    }
  }

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

  // Add circles
  const circles = nodes.append('circle')
    .attr('r', d => d.data.size || nodeRadius)
    .attr('fill', d => colorScale(d.data.type || 'default'))
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .style('cursor', 'pointer')

  // Add hover effects
  circles
    .on('mouseover', function(event, d) {
      d3.select(this)
        .transition()
        .duration(200)
        .attr('r', (d.data.size || nodeRadius) * 1.2)
        .attr('stroke-width', 4)
    })
    .on('mouseout', function(event, d) {
      d3.select(this)
        .transition()
        .duration(200)
        .attr('r', d.data.size || nodeRadius)
        .attr('stroke-width', 2)
    })

  // Add labels (always create but control visibility)
  const labels = nodes.append('text')
    .attr('dy', '0.31em')
    .attr('x', d => d.children ? -6 : 6)
    .attr('text-anchor', d => d.children ? 'end' : 'start')
    .text(d => {
      const text = d.data.name || d.data.label || d.data.id || ''
      return text.length > 15 ? text.substring(0, 12) + '...' : text
    })
    .attr('font-size', '11px')
    .attr('font-weight', 'bold')
    .attr('fill', '#333')
    .attr('pointer-events', 'none')
    .style('display', showLabels ? 'block' : 'none')

  // Helper functions for external control
  const toggleLabels = (show) => {
    labels.style('display', show ? 'block' : 'none')
  }

  const centerGraph = () => {
    // Center the hierarchical view with smooth transition
    svgElement.transition()
      .duration(750)
      .call(zoom.transform, d3.zoomIdentity)
  }

  const updateParameters = (newOptions) => {
    const {
      showLabels: newShowLabels = showLabels,
      nodeRadius: newNodeRadius = nodeRadius
    } = newOptions

    // Update label visibility
    toggleLabels(newShowLabels)

    // Update node sizes
    circles.attr('r', newNodeRadius)
  }

  return {
    root,
    nodes,
    links,
    circles,
    labels,
    toggleLabels,
    centerGraph,
    updateParameters
  }
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
    nodeColors = d3.schemeCategory10,
    showLabels = true
  } = options

  const svgElement = d3.select(svg)
    .attr('width', width)
    .attr('height', height)

  svgElement.selectAll('*').remove()

  // Setup zoom behavior
  const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      g.attr('transform', `translate(${width / 2}, ${height / 2}) ${event.transform}`)
    })

  svgElement.call(zoom)

  const g = svgElement.append('g')
    .attr('transform', `translate(${width / 2}, ${height / 2})`)

  // Validate data
  if (!data || !data.nodes || !Array.isArray(data.nodes) || data.nodes.length === 0) {
    console.error('Invalid data for circular network:', data)
    return { nodes: [], links: [], toggleLabels: () => {}, centerGraph: () => {}, updateParameters: () => {} }
  }

  const nodes = [...data.nodes] // Create copy to avoid mutation
  const links = data.links || []

  // Create node ID map for quick lookup
  const nodeMap = new Map()
  nodes.forEach(node => {
    nodeMap.set(node.id, node)
  })

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

  // Create links with proper error handling
  const validLinks = links.filter(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source
    const targetId = typeof link.target === 'object' ? link.target.id : link.target
    return nodeMap.has(sourceId) && nodeMap.has(targetId)
  })

  const link = g.append('g')
    .attr('class', 'links')
    .selectAll('path')
    .data(validLinks)
    .enter().append('path')
    .attr('d', d => {
      const sourceId = typeof d.source === 'object' ? d.source.id : d.source
      const targetId = typeof d.target === 'object' ? d.target.id : d.target
      const source = nodeMap.get(sourceId)
      const target = nodeMap.get(targetId)

      if (!source || !target) return ''

      // Create curved path
      const dx = target.x - source.x
      const dy = target.y - source.y
      const dr = Math.sqrt(dx * dx + dy * dy) * 0.3
      return `M${source.x},${source.y}A${dr},${dr} 0 0,1 ${target.x},${target.y}`
    })
    .attr('fill', 'none')
    .attr('stroke', '#999')
    .attr('stroke-width', d => Math.sqrt(d.weight || 1) * 2)
    .attr('stroke-opacity', 0.6)

  // Create nodes
  const node = g.append('g')
    .attr('class', 'nodes')
    .selectAll('circle')
    .data(nodes)
    .enter().append('circle')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', d => d.size || nodeRadius)
    .attr('fill', d => colorScale(d.type || 'default'))
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .style('cursor', 'pointer')

  // Add hover effects
  node
    .on('mouseover', function(event, d) {
      d3.select(this)
        .transition()
        .duration(200)
        .attr('r', (d.size || nodeRadius) * 1.2)
        .attr('stroke-width', 4)
    })
    .on('mouseout', function(event, d) {
      d3.select(this)
        .transition()
        .duration(200)
        .attr('r', d.size || nodeRadius)
        .attr('stroke-width', 2)
    })

  // Add labels
  const labels = g.append('g')
    .attr('class', 'labels')
    .selectAll('text')
    .data(nodes)
    .enter().append('text')
    .attr('x', d => d.x)
    .attr('y', d => d.y + (d.size || nodeRadius) + 15)
    .attr('text-anchor', 'middle')
    .attr('font-size', '10px')
    .attr('font-weight', 'bold')
    .attr('fill', '#333')
    .attr('pointer-events', 'none')
    .style('display', showLabels ? 'block' : 'none')
    .text(d => {
      const text = d.label || d.name || d.id || ''
      return text.length > 12 ? text.substring(0, 9) + '...' : text
    })

  // Helper functions for external control
  const toggleLabels = (show) => {
    labels.style('display', show ? 'block' : 'none')
  }

  const centerGraph = () => {
    // Center the circular view with smooth transition
    svgElement.transition()
      .duration(750)
      .call(zoom.transform, d3.zoomIdentity)
  }

  const updateParameters = (newOptions) => {
    const {
      showLabels: newShowLabels = showLabels,
      nodeRadius: newNodeRadius = nodeRadius
    } = newOptions

    // Update label visibility
    toggleLabels(newShowLabels)

    // Update node sizes
    node.attr('r', newNodeRadius)

    // Update label positions
    labels.attr('y', d => d.y + newNodeRadius + 15)
  }

  return {
    nodes,
    links,
    node,
    link,
    labels,
    toggleLabels,
    centerGraph,
    updateParameters
  }
}
