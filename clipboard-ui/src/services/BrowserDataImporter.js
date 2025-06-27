/**
 * Browser Data Import Service
 * Handles importing bookmarks and history from various browsers
 */
class BrowserDataImporter {
  constructor() {
    this.supportedBrowsers = [
      'chrome',
      'firefox', 
      'edge',
      'safari',
      'opera',
      'brave'
    ]
    
    this.supportedFormats = [
      'json',
      'html',
      'csv',
      'netscape'
    ]
  }

  /**
   * Parse Chrome/Chromium bookmarks JSON format
   */
  parseChromeBookmarks(jsonData) {
    try {
      const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData
      const bookmarks = []

      const extractBookmarks = (node, folder = '') => {
        if (node.type === 'url') {
          bookmarks.push({
            url: node.url,
            title: node.name,
            folder: folder,
            dateAdded: node.date_added ? new Date(parseInt(node.date_added) / 1000).toISOString() : new Date().toISOString(),
            id: node.id,
            source: 'chrome'
          })
        } else if (node.type === 'folder' && node.children) {
          const currentFolder = folder ? `${folder}/${node.name}` : node.name
          node.children.forEach(child => extractBookmarks(child, currentFolder))
        }
      }

      // Chrome bookmarks structure
      if (data.roots) {
        Object.values(data.roots).forEach(root => {
          if (root.children) {
            root.children.forEach(child => extractBookmarks(child, root.name || ''))
          }
        })
      }

      return bookmarks
    } catch (error) {
      console.error('Error parsing Chrome bookmarks:', error)
      throw new Error('Invalid Chrome bookmarks format')
    }
  }

  /**
   * Parse Firefox bookmarks JSON format
   */
  parseFirefoxBookmarks(jsonData) {
    try {
      const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData
      const bookmarks = []

      const extractBookmarks = (node, folder = '') => {
        if (node.type === 'text/x-moz-place' && node.uri) {
          bookmarks.push({
            url: node.uri,
            title: node.title || node.uri,
            folder: folder,
            dateAdded: node.dateAdded ? new Date(node.dateAdded / 1000).toISOString() : new Date().toISOString(),
            id: node.id,
            source: 'firefox'
          })
        } else if (node.type === 'text/x-moz-place-container' && node.children) {
          const currentFolder = folder ? `${folder}/${node.title}` : node.title
          node.children.forEach(child => extractBookmarks(child, currentFolder))
        }
      }

      if (Array.isArray(data)) {
        data.forEach(item => extractBookmarks(item))
      } else {
        extractBookmarks(data)
      }

      return bookmarks
    } catch (error) {
      console.error('Error parsing Firefox bookmarks:', error)
      throw new Error('Invalid Firefox bookmarks format')
    }
  }

  /**
   * Parse Netscape HTML bookmark format (universal)
   */
  parseNetscapeBookmarks(htmlContent) {
    try {
      const bookmarks = []
      const parser = new DOMParser()
      const doc = parser.parseFromString(htmlContent, 'text/html')
      
      const links = doc.querySelectorAll('a[href]')
      let currentFolder = ''
      
      // Track folder structure
      const folderStack = []
      
      // Walk through the document to maintain folder context
      const walker = document.createTreeWalker(
        doc.body,
        NodeFilter.SHOW_ELEMENT,
        null,
        false
      )

      let node
      while (node = walker.nextNode()) {
        if (node.tagName === 'H3') {
          // Folder header
          const folderName = node.textContent.trim()
          folderStack.push(folderName)
          currentFolder = folderStack.join('/')
        } else if (node.tagName === 'A' && node.href) {
          // Bookmark link
          const addDate = node.getAttribute('add_date')
          bookmarks.push({
            url: node.href,
            title: node.textContent.trim() || node.href,
            folder: currentFolder,
            dateAdded: addDate ? new Date(parseInt(addDate) * 1000).toISOString() : new Date().toISOString(),
            source: 'netscape_html'
          })
        }
        
        // Handle closing of folders (simplified)
        if (node.tagName === 'DL' && node.parentNode.tagName === 'DD') {
          folderStack.pop()
          currentFolder = folderStack.join('/')
        }
      }

      return bookmarks
    } catch (error) {
      console.error('Error parsing Netscape bookmarks:', error)
      throw new Error('Invalid Netscape HTML format')
    }
  }

  /**
   * Parse CSV bookmark format
   */
  parseCSVBookmarks(csvContent) {
    try {
      const lines = csvContent.split('\n')
      const bookmarks = []
      
      // Skip header if present
      const startIndex = lines[0].toLowerCase().includes('url') || lines[0].toLowerCase().includes('title') ? 1 : 0
      
      for (let i = startIndex; i < lines.length; i++) {
        const line = lines[i].trim()
        if (!line) continue
        
        // Simple CSV parsing (handles quoted fields)
        const fields = this.parseCSVLine(line)
        
        if (fields.length >= 2) {
          bookmarks.push({
            url: fields[0],
            title: fields[1] || fields[0],
            folder: fields[2] || 'Imported',
            dateAdded: fields[3] ? new Date(fields[3]).toISOString() : new Date().toISOString(),
            source: 'csv'
          })
        }
      }

      return bookmarks
    } catch (error) {
      console.error('Error parsing CSV bookmarks:', error)
      throw new Error('Invalid CSV format')
    }
  }

  /**
   * Parse Chrome history JSON format
   */
  parseChromeHistory(jsonData) {
    try {
      const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData
      const history = []

      if (Array.isArray(data)) {
        data.forEach(item => {
          if (item.url) {
            history.push({
              url: item.url,
              title: item.title || item.url,
              visitTime: item.last_visit_time ? new Date(parseInt(item.last_visit_time) / 1000).toISOString() : new Date().toISOString(),
              visitCount: item.visit_count || 1,
              source: 'chrome_history'
            })
          }
        })
      }

      return history
    } catch (error) {
      console.error('Error parsing Chrome history:', error)
      throw new Error('Invalid Chrome history format')
    }
  }

  /**
   * Auto-detect format and parse accordingly
   */
  autoDetectAndParse(content, filename = '') {
    try {
      const extension = filename.split('.').pop().toLowerCase()
      const trimmedContent = content.trim()

      // Try JSON first
      if (trimmedContent.startsWith('{') || trimmedContent.startsWith('[')) {
        try {
          const jsonData = JSON.parse(trimmedContent)
          
          // Detect Chrome bookmarks
          if (jsonData.roots && jsonData.version) {
            return {
              type: 'bookmarks',
              format: 'chrome',
              data: this.parseChromeBookmarks(jsonData)
            }
          }
          
          // Detect Firefox bookmarks
          if (jsonData.type === 'text/x-moz-place-container' || 
              (Array.isArray(jsonData) && jsonData[0]?.type?.includes('moz'))) {
            return {
              type: 'bookmarks', 
              format: 'firefox',
              data: this.parseFirefoxBookmarks(jsonData)
            }
          }
          
          // Detect Chrome history
          if (Array.isArray(jsonData) && jsonData[0]?.url && jsonData[0]?.last_visit_time) {
            return {
              type: 'history',
              format: 'chrome',
              data: this.parseChromeHistory(jsonData)
            }
          }
          
          // Generic JSON array
          if (Array.isArray(jsonData)) {
            return {
              type: 'bookmarks',
              format: 'generic_json',
              data: jsonData.map(item => ({
                url: item.url || item.href,
                title: item.title || item.name || item.url,
                folder: item.folder || 'Imported',
                dateAdded: item.dateAdded || item.date || new Date().toISOString(),
                source: 'generic_json'
              }))
            }
          }
        } catch (e) {
          // Not valid JSON, continue to other formats
        }
      }

      // Try HTML (Netscape format)
      if (trimmedContent.includes('<html') || trimmedContent.includes('<!DOCTYPE') || 
          trimmedContent.includes('<a href') || extension === 'html') {
        return {
          type: 'bookmarks',
          format: 'netscape',
          data: this.parseNetscapeBookmarks(trimmedContent)
        }
      }

      // Try CSV
      if (trimmedContent.includes(',') || extension === 'csv') {
        return {
          type: 'bookmarks',
          format: 'csv', 
          data: this.parseCSVBookmarks(trimmedContent)
        }
      }

      throw new Error('Unable to detect format')
    } catch (error) {
      console.error('Error auto-detecting format:', error)
      throw new Error(`Unable to parse file: ${error.message}`)
    }
  }

  /**
   * Parse CSV line handling quoted fields
   */
  parseCSVLine(line) {
    const fields = []
    let current = ''
    let inQuotes = false
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i]
      
      if (char === '"') {
        inQuotes = !inQuotes
      } else if (char === ',' && !inQuotes) {
        fields.push(current.trim())
        current = ''
      } else {
        current += char
      }
    }
    
    fields.push(current.trim())
    return fields
  }

  /**
   * Validate imported data
   */
  validateImportedData(data) {
    const errors = []
    const warnings = []
    
    if (!Array.isArray(data) || data.length === 0) {
      errors.push('No valid data found')
      return { valid: false, errors, warnings }
    }

    let validEntries = 0
    data.forEach((item, index) => {
      if (!item.url || typeof item.url !== 'string') {
        warnings.push(`Entry ${index + 1}: Missing or invalid URL`)
      } else if (!item.url.startsWith('http://') && !item.url.startsWith('https://')) {
        warnings.push(`Entry ${index + 1}: URL may be invalid (${item.url})`)
      } else {
        validEntries++
      }
    })

    if (validEntries === 0) {
      errors.push('No entries with valid URLs found')
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      validEntries,
      totalEntries: data.length
    }
  }

  /**
   * Get import statistics
   */
  getImportStats(data) {
    const stats = {
      total: data.length,
      bySource: {},
      byFolder: {},
      urlDomains: {},
      dateRange: { earliest: null, latest: null }
    }

    data.forEach(item => {
      // Count by source
      stats.bySource[item.source] = (stats.bySource[item.source] || 0) + 1
      
      // Count by folder
      const folder = item.folder || 'Unknown'
      stats.byFolder[folder] = (stats.byFolder[folder] || 0) + 1
      
      // Count by domain
      try {
        const domain = new URL(item.url).hostname
        stats.urlDomains[domain] = (stats.urlDomains[domain] || 0) + 1
      } catch (e) {
        // Invalid URL
      }
      
      // Track date range
      if (item.dateAdded) {
        const date = new Date(item.dateAdded)
        if (!stats.dateRange.earliest || date < new Date(stats.dateRange.earliest)) {
          stats.dateRange.earliest = item.dateAdded
        }
        if (!stats.dateRange.latest || date > new Date(stats.dateRange.latest)) {
          stats.dateRange.latest = item.dateAdded
        }
      }
    })

    return stats
  }

  /**
   * Generate sample data for testing
   */
  generateSampleData(type = 'bookmarks', count = 10) {
    const sampleData = []
    const domains = ['github.com', 'stackoverflow.com', 'developer.mozilla.org', 'google.com', 'youtube.com']
    const folders = ['Development', 'Reference', 'Entertainment', 'News', 'Tools']
    
    for (let i = 0; i < count; i++) {
      const domain = domains[Math.floor(Math.random() * domains.length)]
      const folder = folders[Math.floor(Math.random() * folders.length)]
      
      if (type === 'bookmarks') {
        sampleData.push({
          url: `https://${domain}/sample-page-${i}`,
          title: `Sample Page ${i} - ${domain}`,
          folder: folder,
          dateAdded: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
          source: 'sample_data'
        })
      } else if (type === 'history') {
        sampleData.push({
          url: `https://${domain}/visited-page-${i}`,
          title: `Visited Page ${i} - ${domain}`,
          visitTime: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
          visitCount: Math.floor(Math.random() * 10) + 1,
          source: 'sample_data'
        })
      }
    }
    
    return sampleData
  }
}

export default new BrowserDataImporter()
