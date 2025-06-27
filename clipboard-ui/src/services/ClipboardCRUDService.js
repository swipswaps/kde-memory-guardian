/**
 * Professional Clipboard CRUD Service
 * Provides comprehensive Create, Read, Update, Delete operations for clipboard data
 * Works with actual system clipboard data, not mock/sample data
 */
class ClipboardCRUDService {
  constructor() {
    this.baseURL = 'http://localhost:3001/api/clipboard'
    this.cache = new Map()
    this.cacheTimeout = 30000 // 30 seconds
  }

  // ==================== READ OPERATIONS ====================

  /**
   * Get clipboard history with pagination and filtering
   * @param {Object} options - Query options
   * @returns {Promise<Array>} Clipboard entries
   */
  async getHistory(options = {}) {
    const {
      limit = 100,
      offset = 0,
      contentType = null,
      dateFrom = null,
      dateTo = null,
      search = null,
      sortBy = 'timestamp',
      sortOrder = 'desc'
    } = options

    try {
      const params = new URLSearchParams()
      if (limit) params.append('limit', limit)
      if (offset) params.append('offset', offset)
      if (contentType) params.append('content_type', contentType)
      if (dateFrom) params.append('date_from', dateFrom)
      if (dateTo) params.append('date_to', dateTo)
      if (search) params.append('search', search)
      if (sortBy) params.append('sort_by', sortBy)
      if (sortOrder) params.append('sort_order', sortOrder)

      const cacheKey = `history_${params.toString()}`
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey)
        if (Date.now() - cached.timestamp < this.cacheTimeout) {
          return cached.data
        }
      }

      const response = await fetch(`${this.baseURL}/history?${params.toString()}`)
      if (!response.ok) {
        throw new Error(`Failed to fetch clipboard history: ${response.status}`)
      }

      const data = await response.json()
      
      // Cache the result
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      })

      return data
    } catch (error) {
      console.error('Error fetching clipboard history:', error)
      throw error
    }
  }

  /**
   * Get a specific clipboard entry by ID
   * @param {string} id - Entry ID
   * @returns {Promise<Object>} Clipboard entry
   */
  async getEntry(id) {
    try {
      const response = await fetch(`${this.baseURL}/entry/${id}`)
      if (!response.ok) {
        throw new Error(`Failed to fetch clipboard entry: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching clipboard entry:', error)
      throw error
    }
  }

  /**
   * Get clipboard statistics and analytics
   * @returns {Promise<Object>} Statistics object
   */
  async getStatistics() {
    try {
      const response = await fetch(`${this.baseURL}/statistics`)
      if (!response.ok) {
        throw new Error(`Failed to fetch statistics: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching statistics:', error)
      throw error
    }
  }

  /**
   * Get content type distribution
   * @returns {Promise<Array>} Content type counts
   */
  async getContentTypeDistribution() {
    try {
      const response = await fetch(`${this.baseURL}/content-types`)
      if (!response.ok) {
        throw new Error(`Failed to fetch content types: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching content types:', error)
      throw error
    }
  }

  // ==================== CREATE OPERATIONS ====================

  /**
   * Create a new clipboard entry
   * @param {Object} entry - Entry data
   * @returns {Promise<Object>} Created entry
   */
  async createEntry(entry) {
    try {
      this.validateEntry(entry)

      const entryData = {
        content: entry.content,
        content_type: entry.content_type || this.detectContentType(entry.content),
        timestamp: entry.timestamp || new Date().toISOString(),
        size_bytes: new Blob([entry.content]).size,
        source: entry.source || 'manual',
        tags: entry.tags || [],
        category: entry.category || this.detectCategory(entry.content),
        metadata: entry.metadata || {}
      }

      const response = await fetch(`${this.baseURL}/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entryData)
      })

      if (!response.ok) {
        throw new Error(`Failed to create clipboard entry: ${response.status}`)
      }

      const result = await response.json()
      this.clearCache() // Clear cache after modification
      return result
    } catch (error) {
      console.error('Error creating clipboard entry:', error)
      throw error
    }
  }

  /**
   * Bulk create multiple clipboard entries
   * @param {Array} entries - Array of entry objects
   * @returns {Promise<Object>} Bulk creation result
   */
  async bulkCreateEntries(entries) {
    try {
      entries.forEach(entry => this.validateEntry(entry))

      const response = await fetch(`${this.baseURL}/bulk-create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ entries })
      })

      if (!response.ok) {
        throw new Error(`Failed to bulk create entries: ${response.status}`)
      }

      const result = await response.json()
      this.clearCache()
      return result
    } catch (error) {
      console.error('Error bulk creating entries:', error)
      throw error
    }
  }

  // ==================== UPDATE OPERATIONS ====================

  /**
   * Update a clipboard entry
   * @param {string} id - Entry ID
   * @param {Object} updates - Fields to update
   * @returns {Promise<Object>} Updated entry
   */
  async updateEntry(id, updates) {
    try {
      const updateData = {
        ...updates,
        updated_at: new Date().toISOString()
      }

      const response = await fetch(`${this.baseURL}/entry/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
      })

      if (!response.ok) {
        throw new Error(`Failed to update clipboard entry: ${response.status}`)
      }

      const result = await response.json()
      this.clearCache()
      return result
    } catch (error) {
      console.error('Error updating clipboard entry:', error)
      throw error
    }
  }

  /**
   * Update entry tags
   * @param {string} id - Entry ID
   * @param {Array} tags - New tags array
   * @returns {Promise<Object>} Updated entry
   */
  async updateTags(id, tags) {
    return this.updateEntry(id, { tags })
  }

  /**
   * Update entry category
   * @param {string} id - Entry ID
   * @param {string} category - New category
   * @returns {Promise<Object>} Updated entry
   */
  async updateCategory(id, category) {
    return this.updateEntry(id, { category })
  }

  /**
   * Bulk update multiple entries
   * @param {Array} updates - Array of {id, updates} objects
   * @returns {Promise<Object>} Bulk update result
   */
  async bulkUpdateEntries(updates) {
    try {
      const response = await fetch(`${this.baseURL}/bulk-update`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ updates })
      })

      if (!response.ok) {
        throw new Error(`Failed to bulk update entries: ${response.status}`)
      }

      const result = await response.json()
      this.clearCache()
      return result
    } catch (error) {
      console.error('Error bulk updating entries:', error)
      throw error
    }
  }

  // ==================== DELETE OPERATIONS ====================

  /**
   * Delete a clipboard entry
   * @param {string} id - Entry ID
   * @returns {Promise<Object>} Deletion result
   */
  async deleteEntry(id) {
    try {
      const response = await fetch(`${this.baseURL}/entry/${id}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error(`Failed to delete clipboard entry: ${response.status}`)
      }

      const result = await response.json()
      this.clearCache()
      return result
    } catch (error) {
      console.error('Error deleting clipboard entry:', error)
      throw error
    }
  }

  /**
   * Bulk delete multiple entries
   * @param {Array} ids - Array of entry IDs
   * @returns {Promise<Object>} Bulk deletion result
   */
  async bulkDeleteEntries(ids) {
    try {
      const response = await fetch(`${this.baseURL}/bulk-delete`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids })
      })

      if (!response.ok) {
        throw new Error(`Failed to bulk delete entries: ${response.status}`)
      }

      const result = await response.json()
      this.clearCache()
      return result
    } catch (error) {
      console.error('Error bulk deleting entries:', error)
      throw error
    }
  }

  /**
   * Clear clipboard history with optional date filter
   * @param {string} beforeDate - Optional date to clear entries before
   * @returns {Promise<Object>} Clear result
   */
  async clearHistory(beforeDate = null) {
    try {
      const url = beforeDate 
        ? `${this.baseURL}/clear?before=${encodeURIComponent(beforeDate)}`
        : `${this.baseURL}/clear`

      const response = await fetch(url, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error(`Failed to clear clipboard history: ${response.status}`)
      }

      const result = await response.json()
      this.clearCache()
      return result
    } catch (error) {
      console.error('Error clearing clipboard history:', error)
      throw error
    }
  }

  // ==================== SEARCH OPERATIONS ====================

  /**
   * Advanced search with multiple filters
   * @param {Object} searchParams - Search parameters
   * @returns {Promise<Array>} Search results
   */
  async search(searchParams) {
    const {
      query = '',
      contentType = null,
      category = null,
      tags = [],
      dateFrom = null,
      dateTo = null,
      minSize = null,
      maxSize = null,
      limit = 100,
      offset = 0
    } = searchParams

    try {
      const params = new URLSearchParams()
      if (query) params.append('q', query)
      if (contentType) params.append('content_type', contentType)
      if (category) params.append('category', category)
      if (tags.length > 0) params.append('tags', tags.join(','))
      if (dateFrom) params.append('date_from', dateFrom)
      if (dateTo) params.append('date_to', dateTo)
      if (minSize) params.append('min_size', minSize)
      if (maxSize) params.append('max_size', maxSize)
      if (limit) params.append('limit', limit)
      if (offset) params.append('offset', offset)

      const response = await fetch(`${this.baseURL}/search?${params.toString()}`)
      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error searching clipboard entries:', error)
      throw error
    }
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Validate clipboard entry data
   * @param {Object} entry - Entry to validate
   * @throws {Error} If validation fails
   */
  validateEntry(entry) {
    if (!entry.content || typeof entry.content !== 'string') {
      throw new Error('Content is required and must be a string')
    }
    if (entry.content.trim() === '') {
      throw new Error('Content cannot be empty')
    }
    if (entry.content.length > 10000000) { // 10MB limit
      throw new Error('Content too large (max 10MB)')
    }
  }

  /**
   * Detect content type from content
   * @param {string} content - Content to analyze
   * @returns {string} Detected content type
   */
  detectContentType(content) {
    const trimmed = content.trim()
    
    if (trimmed.startsWith('{') && trimmed.endsWith('}')) return 'JSON'
    if (trimmed.startsWith('[') && trimmed.endsWith(']')) return 'JSON'
    if (content.includes('http://') || content.includes('https://')) return 'URL'
    if (content.includes(',') && content.includes('\n')) return 'CSV'
    if (content.includes('@') && content.includes('.')) return 'Email'
    if (/^\d+$/.test(trimmed)) return 'Number'
    if (content.includes('<') && content.includes('>')) return 'HTML'
    
    return 'Text'
  }

  /**
   * Detect category from content and type
   * @param {string} content - Content to analyze
   * @returns {string} Detected category
   */
  detectCategory(content) {
    const contentType = this.detectContentType(content)
    
    if (contentType === 'URL') return 'web'
    if (contentType === 'JSON') return 'data'
    if (contentType === 'CSV') return 'spreadsheet'
    if (contentType === 'Email') return 'communication'
    if (contentType === 'Number') return 'numeric'
    if (contentType === 'HTML') return 'markup'
    
    return 'general'
  }

  /**
   * Clear internal cache
   */
  clearCache() {
    this.cache.clear()
  }

  /**
   * Format bytes to human readable string
   * @param {number} bytes - Bytes to format
   * @returns {string} Formatted string
   */
  formatBytes(bytes) {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }
}

export default new ClipboardCRUDService()
