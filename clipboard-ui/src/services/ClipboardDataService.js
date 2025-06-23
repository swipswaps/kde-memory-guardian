class ClipboardDataService {
  constructor() {
    this.apiBaseUrl = 'http://localhost:3001/api'
  }

  // Get clipboard history from our SQL system via API
  async getClipboardHistory(limit = 100) {
    console.log('ClipboardDataService: Fetching data from API...')

    // First try the API
    try {
      const url = `${this.apiBaseUrl}/clipboard/history?limit=${limit}`
      console.log('ClipboardDataService: Fetching from URL:', url)

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors'
      })

      console.log('ClipboardDataService: Response status:', response.status)

      if (response.ok) {
        const data = await response.json()
        console.log('ClipboardDataService: Received data from API:', data.length, 'entries')

        // Ensure data has the right format
        if (Array.isArray(data) && data.length > 0) {
          return data
        }
      }

      throw new Error(`API request failed: ${response.status}`)
    } catch (error) {
      console.error('ClipboardDataService: API failed, using mock data:', error)

      // Return enhanced mock data that definitely works
      const mockData = this.getMockData()
      console.log('ClipboardDataService: Returning mock data:', mockData.length, 'entries')
      return mockData
    }
  }

  // Web-based clipboard history (using localStorage for demo)
  getClipboardHistoryWeb(limit = 100) {
    const stored = localStorage.getItem('clipboard_history')
    if (stored) {
      return JSON.parse(stored).slice(0, limit)
    }
    
    // Generate mock data if no stored data
    return this.getMockData()
  }

  // Generate comprehensive mock data for demonstration
  getMockData() {
    const mockData = [
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
        content: '{"tasks": [{"name": "Design UI", "start": "2024-01-01", "end": "2024-01-15", "progress": 0.8}, {"name": "Backend API", "start": "2024-01-10", "end": "2024-01-25", "progress": 0.6}, {"name": "Testing", "start": "2024-01-20", "end": "2024-02-05", "progress": 0.3}]}',
        size_bytes: 200
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        content_type: 'Text',
        content: 'Q1 Revenue: $125,000\nQ2 Revenue: $150,000\nQ3 Revenue: $175,000\nQ4 Revenue: $200,000',
        size_bytes: 85
      },
      {
        id: '4',
        timestamp: new Date(Date.now() - 10800000).toISOString(),
        content_type: 'Text',
        content: 'https://github.com/d3/d3\nhttps://material-ui.com\nhttps://reactjs.org\nhttps://vitejs.dev',
        size_bytes: 95
      },
      {
        id: '5',
        timestamp: new Date(Date.now() - 14400000).toISOString(),
        content_type: 'Text',
        content: 'Team,Members,Budget\nEngineering,12,500000\nDesign,5,200000\nMarketing,8,300000\nSales,15,400000',
        size_bytes: 105
      },
      {
        id: '6',
        timestamp: new Date(Date.now() - 18000000).toISOString(),
        content_type: 'Text',
        content: '{"metrics": {"cpu": 75, "memory": 60, "disk": 45, "network": 30}}',
        size_bytes: 70
      },
      {
        id: '7',
        timestamp: new Date(Date.now() - 21600000).toISOString(),
        content_type: 'Text',
        content: 'JavaScript frameworks comparison:\nReact: 85% satisfaction\nVue: 78% satisfaction\nAngular: 65% satisfaction\nSvelte: 92% satisfaction',
        size_bytes: 140
      }
    ]

    // Store in localStorage for persistence
    if (typeof window !== 'undefined') {
      localStorage.setItem('clipboard_history', JSON.stringify(mockData))
    }

    return mockData
  }

  // Process clipboard data for different chart types
  async processDataForVisualization(data, chartType) {
    const processedData = []

    for (const item of data) {
      const processed = this.parseClipboardContent(item.content, chartType)
      if (processed && processed.length > 0) {
        processedData.push({
          ...item,
          parsedData: processed,
          chartType: this.detectBestChartType(processed)
        })
      }
    }

    return this.formatDataForChart(processedData, chartType)
  }

  // Parse different content types
  parseClipboardContent(content, chartType) {
    // Try JSON first
    if (content.trim().startsWith('{') || content.trim().startsWith('[')) {
      try {
        const jsonData = JSON.parse(content)
        return this.extractDataFromJSON(jsonData, chartType)
      } catch (e) {
        // Not valid JSON, continue
      }
    }

    // Try CSV
    if (content.includes(',') && content.includes('\n')) {
      return this.parseCSVData(content)
    }

    // Try key-value pairs
    if (content.includes(':') && content.includes('\n')) {
      return this.parseKeyValueData(content)
    }

    // Try URLs
    if (content.includes('http')) {
      return this.parseURLData(content)
    }

    // Try numbers and text
    return this.parseTextData(content)
  }

  // Parse CSV data
  parseCSVData(content) {
    const lines = content.trim().split('\n')
    if (lines.length < 2) return null

    const headers = lines[0].split(',').map(h => h.trim())
    const data = []

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim())
      if (values.length === headers.length) {
        const row = {}
        headers.forEach((header, index) => {
          const value = values[index]
          row[header] = isNaN(value) ? value : parseFloat(value)
        })
        data.push(row)
      }
    }

    return data
  }

  // Parse JSON data
  extractDataFromJSON(jsonData, chartType) {
    if (Array.isArray(jsonData)) {
      return jsonData
    }

    if (typeof jsonData === 'object') {
      // Convert object to array of key-value pairs
      return Object.entries(jsonData).map(([key, value]) => ({
        label: key,
        value: typeof value === 'number' ? value : 1,
        category: typeof value === 'object' ? JSON.stringify(value) : String(value)
      }))
    }

    return null
  }

  // Parse key-value data
  parseKeyValueData(content) {
    const lines = content.split('\n').filter(line => line.includes(':'))
    return lines.map(line => {
      const [key, ...valueParts] = line.split(':')
      const value = valueParts.join(':').trim()
      const numValue = parseFloat(value.replace(/[^0-9.-]/g, ''))
      
      return {
        label: key.trim(),
        value: isNaN(numValue) ? 1 : numValue,
        category: value
      }
    })
  }

  // Parse URL data
  parseURLData(content) {
    const urls = content.match(/https?:\/\/[^\s]+/g) || []
    const domains = urls.map(url => {
      try {
        return new URL(url).hostname
      } catch {
        return url
      }
    })

    // Count domain frequency
    const domainCounts = {}
    domains.forEach(domain => {
      domainCounts[domain] = (domainCounts[domain] || 0) + 1
    })

    return Object.entries(domainCounts).map(([domain, count]) => ({
      label: domain,
      value: count,
      category: 'URL'
    }))
  }

  // Parse general text data
  parseTextData(content) {
    // Extract numbers and create simple data
    const numbers = content.match(/\d+/g)
    if (numbers && numbers.length > 1) {
      return numbers.map((num, index) => ({
        label: `Item ${index + 1}`,
        value: parseInt(num),
        category: 'Number'
      }))
    }

    // Word frequency for text
    const words = content.toLowerCase().split(/\s+/).filter(word => word.length > 3)
    const wordCounts = {}
    words.forEach(word => {
      wordCounts[word] = (wordCounts[word] || 0) + 1
    })

    return Object.entries(wordCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([word, count]) => ({
        label: word,
        value: count,
        category: 'Word'
      }))
  }

  // Detect best chart type for data
  detectBestChartType(data) {
    if (!data || data.length === 0) return 'bar'

    const hasTimeData = data.some(item => 
      item.start || item.end || item.date || 
      (typeof item.label === 'string' && item.label.match(/\d{4}-\d{2}-\d{2}/))
    )

    if (hasTimeData) return 'gantt'

    const hasCategories = data.some(item => item.category)
    const isNumeric = data.every(item => typeof item.value === 'number')

    if (data.length <= 6 && isNumeric) return 'pie'
    if (data.length > 20) return 'scatter'
    if (hasCategories) return 'bubble'

    return 'bar'
  }

  // Format data for specific chart types
  formatDataForChart(processedData, chartType) {
    if (!processedData || processedData.length === 0) return null

    // Combine all parsed data
    const allData = processedData.flatMap(item => item.parsedData || [])
    
    switch (chartType) {
      case 'pie':
      case 'donut':
        return this.formatForPieChart(allData)
      case 'bar':
        return this.formatForBarChart(allData)
      case 'line':
        return this.formatForLineChart(allData)
      case 'scatter':
        return this.formatForScatterPlot(allData)
      case 'bubble':
        return this.formatForBubbleChart(allData)
      case 'gantt':
        return this.formatForGanttChart(processedData)
      case 'treemap':
        return this.formatForTreemap(allData)
      case 'heatmap':
        return this.formatForHeatmap(allData)
      case 'wordcloud':
        return this.formatForWordCloud(processedData)
      default:
        return allData
    }
  }

  formatForPieChart(data) {
    return data.slice(0, 8).map(item => ({
      label: item.label,
      value: Math.abs(item.value) || 1
    }))
  }

  formatForBarChart(data) {
    return data.slice(0, 15).map(item => ({
      label: item.label,
      value: item.value || 0
    }))
  }

  formatForLineChart(data) {
    return data.map((item, index) => ({
      x: index,
      y: item.value || 0,
      label: item.label
    }))
  }

  formatForScatterPlot(data) {
    return data.map((item, index) => ({
      x: index,
      y: item.value || 0,
      label: item.label,
      category: item.category
    }))
  }

  formatForBubbleChart(data) {
    return data.map((item, index) => ({
      x: index,
      y: item.value || 0,
      r: Math.abs(item.value) / 10 + 5,
      label: item.label,
      category: item.category
    }))
  }

  formatForGanttChart(processedData) {
    // Look for data with start/end dates
    const ganttData = []
    
    processedData.forEach(item => {
      if (item.content.includes('start') && item.content.includes('end')) {
        try {
          const jsonData = JSON.parse(item.content)
          if (jsonData.tasks) {
            ganttData.push(...jsonData.tasks)
          }
        } catch (e) {
          // Try to parse as text
          const lines = item.content.split('\n')
          lines.forEach(line => {
            if (line.includes('start') || line.includes('end')) {
              ganttData.push({
                name: line.split(':')[0] || 'Task',
                start: '2024-01-01',
                end: '2024-01-15',
                progress: Math.random()
              })
            }
          })
        }
      }
    })

    return ganttData.length > 0 ? ganttData : [
      { name: 'Sample Task', start: '2024-01-01', end: '2024-01-15', progress: 0.7 }
    ]
  }

  formatForWordCloud(data) {
    // Combine all text content for word frequency analysis
    const allText = data.map(item => item.content).join(' ')
    const words = this.extractWordFrequency(allText)

    return words.slice(0, 50).map(([word, count]) => ({
      text: word,
      value: count,
      size: Math.max(12, Math.min(48, count * 4))
    }))
  }

  extractWordFrequency(text) {
    const stopWords = new Set([
      'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
      'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
      'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
      'those', 'a', 'an', 'it', 'its', 'they', 'them', 'their', 'there', 'then', 'than',
      'when', 'where', 'why', 'how', 'what', 'who', 'which', 'whose', 'whom', 'all', 'any',
      'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
      'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'
    ])

    const wordCounts = {}

    text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 3 && !stopWords.has(word))
      .forEach(word => {
        wordCounts[word] = (wordCounts[word] || 0) + 1
      })

    return Object.entries(wordCounts).sort(([,a], [,b]) => b - a)
  }

  formatForTreemap(data) {
    return {
      name: 'root',
      children: data.slice(0, 10).map(item => ({
        name: item.label,
        value: Math.abs(item.value) || 1
      }))
    }
  }

  formatForHeatmap(data) {
    const matrix = []
    const size = Math.min(Math.ceil(Math.sqrt(data.length)), 10)
    
    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        const index = i * size + j
        matrix.push({
          x: j,
          y: i,
          value: data[index]?.value || 0,
          label: data[index]?.label || `${i},${j}`
        })
      }
    }
    
    return matrix
  }
}

export default new ClipboardDataService()
