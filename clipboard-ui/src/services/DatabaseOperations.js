import DatabaseRegistry from './DatabaseRegistry'

/**
 * Database Operations Service
 * Provides unified CRUD operations across multiple registered databases
 */
class DatabaseOperations {
  constructor() {
    this.registry = DatabaseRegistry
  }

  /**
   * Initialize database operations
   */
  async initialize() {
    return await this.registry.initializeRegistry()
  }

  /**
   * Generic create operation
   */
  async create(databaseId, storeName, data) {
    try {
      const db = this.registry.getActiveDatabase(databaseId)
      if (!db) {
        throw new Error(`Database '${databaseId}' is not connected`)
      }

      const entry = {
        ...data,
        created: new Date().toISOString(),
        modified: new Date().toISOString()
      }

      const tx = db.transaction(storeName, 'readwrite')
      const result = await tx.objectStore(storeName).add(entry)
      await tx.complete

      console.log(`Created entry in ${databaseId}.${storeName}:`, result)
      return result
    } catch (error) {
      console.error('Error creating entry:', error)
      throw error
    }
  }

  /**
   * Generic read operation with filtering
   */
  async read(databaseId, storeName, options = {}) {
    try {
      const db = this.registry.getActiveDatabase(databaseId)
      if (!db) {
        throw new Error(`Database '${databaseId}' is not connected`)
      }

      const {
        limit = 100,
        offset = 0,
        indexName = null,
        indexValue = null,
        filter = null,
        sortBy = null,
        sortOrder = 'asc'
      } = options

      const tx = db.transaction(storeName, 'readonly')
      const store = tx.objectStore(storeName)
      
      let cursor
      if (indexName && indexValue) {
        const index = store.index(indexName)
        cursor = await index.openCursor(indexValue)
      } else {
        cursor = await store.openCursor()
      }

      const results = []
      let count = 0
      let skipped = 0

      while (cursor && results.length < limit) {
        const entry = cursor.value

        // Apply filter if provided
        let include = true
        if (filter && typeof filter === 'function') {
          include = filter(entry)
        }

        if (include) {
          if (skipped >= offset) {
            results.push(entry)
          } else {
            skipped++
          }
        }

        cursor = await cursor.continue()
        count++
      }

      // Apply sorting if requested
      if (sortBy && results.length > 0) {
        results.sort((a, b) => {
          const aVal = a[sortBy]
          const bVal = b[sortBy]
          
          if (sortOrder === 'desc') {
            return bVal > aVal ? 1 : bVal < aVal ? -1 : 0
          } else {
            return aVal > bVal ? 1 : aVal < bVal ? -1 : 0
          }
        })
      }

      await tx.complete

      return {
        data: results,
        total: count,
        hasMore: cursor !== null
      }
    } catch (error) {
      console.error('Error reading entries:', error)
      throw error
    }
  }

  /**
   * Generic update operation
   */
  async update(databaseId, storeName, id, updates) {
    try {
      const db = this.registry.getActiveDatabase(databaseId)
      if (!db) {
        throw new Error(`Database '${databaseId}' is not connected`)
      }

      const tx = db.transaction(storeName, 'readwrite')
      const store = tx.objectStore(storeName)
      
      const existing = await store.get(id)
      if (!existing) {
        throw new Error(`Entry with id ${id} not found in ${databaseId}.${storeName}`)
      }

      const updated = {
        ...existing,
        ...updates,
        modified: new Date().toISOString()
      }

      await store.put(updated)
      await tx.complete
      
      console.log(`Updated entry in ${databaseId}.${storeName}:`, id)
      return updated
    } catch (error) {
      console.error('Error updating entry:', error)
      throw error
    }
  }

  /**
   * Generic delete operation
   */
  async delete(databaseId, storeName, id) {
    try {
      const db = this.registry.getActiveDatabase(databaseId)
      if (!db) {
        throw new Error(`Database '${databaseId}' is not connected`)
      }

      const tx = db.transaction(storeName, 'readwrite')
      await tx.objectStore(storeName).delete(id)
      await tx.complete
      
      console.log(`Deleted entry from ${databaseId}.${storeName}:`, id)
      return true
    } catch (error) {
      console.error('Error deleting entry:', error)
      throw error
    }
  }

  /**
   * Bulk operations
   */
  async bulkCreate(databaseId, storeName, dataArray) {
    try {
      const db = this.registry.getActiveDatabase(databaseId)
      if (!db) {
        throw new Error(`Database '${databaseId}' is not connected`)
      }

      const tx = db.transaction(storeName, 'readwrite')
      const store = tx.objectStore(storeName)
      
      const results = []
      for (const data of dataArray) {
        const entry = {
          ...data,
          created: new Date().toISOString(),
          modified: new Date().toISOString()
        }
        const result = await store.add(entry)
        results.push(result)
      }
      
      await tx.complete
      console.log(`Bulk created ${results.length} entries in ${databaseId}.${storeName}`)
      return results
    } catch (error) {
      console.error('Error bulk creating entries:', error)
      throw error
    }
  }

  async bulkDelete(databaseId, storeName, ids) {
    try {
      const db = this.registry.getActiveDatabase(databaseId)
      if (!db) {
        throw new Error(`Database '${databaseId}' is not connected`)
      }

      const tx = db.transaction(storeName, 'readwrite')
      const store = tx.objectStore(storeName)
      
      for (const id of ids) {
        await store.delete(id)
      }
      
      await tx.complete
      console.log(`Bulk deleted ${ids.length} entries from ${databaseId}.${storeName}`)
      return true
    } catch (error) {
      console.error('Error bulk deleting entries:', error)
      throw error
    }
  }

  /**
   * Search across multiple databases
   */
  async search(searchTerm, options = {}) {
    try {
      const {
        databases = null, // null means search all active databases
        stores = null,    // null means search all stores
        fields = ['title', 'content', 'name', 'description'],
        limit = 100
      } = options

      const activeDatabases = databases || Array.from(this.registry.activeDatabases.keys())
      const results = []

      for (const databaseId of activeDatabases) {
        const dbInfo = await this.registry.getDatabaseInfo(databaseId)
        if (!dbInfo) continue

        const searchStores = stores || Object.keys(dbInfo.stores)

        for (const storeName of searchStores) {
          try {
            const storeResults = await this.read(databaseId, storeName, {
              limit: limit,
              filter: (entry) => {
                return fields.some(field => {
                  const value = entry[field]
                  return value && typeof value === 'string' && 
                         value.toLowerCase().includes(searchTerm.toLowerCase())
                })
              }
            })

            storeResults.data.forEach(entry => {
              results.push({
                ...entry,
                _source: {
                  database: databaseId,
                  store: storeName,
                  databaseName: dbInfo.name
                }
              })
            })
          } catch (error) {
            console.warn(`Error searching in ${databaseId}.${storeName}:`, error)
          }
        }
      }

      // Sort by relevance (simple scoring based on field matches)
      results.sort((a, b) => {
        const aScore = this.calculateRelevanceScore(a, searchTerm, fields)
        const bScore = this.calculateRelevanceScore(b, searchTerm, fields)
        return bScore - aScore
      })

      return results.slice(0, limit)
    } catch (error) {
      console.error('Error searching databases:', error)
      throw error
    }
  }

  /**
   * Calculate relevance score for search results
   */
  calculateRelevanceScore(entry, searchTerm, fields) {
    let score = 0
    const term = searchTerm.toLowerCase()

    fields.forEach(field => {
      const value = entry[field]
      if (value && typeof value === 'string') {
        const lowerValue = value.toLowerCase()
        
        // Exact match gets highest score
        if (lowerValue === term) {
          score += 100
        }
        // Starts with term gets high score
        else if (lowerValue.startsWith(term)) {
          score += 50
        }
        // Contains term gets medium score
        else if (lowerValue.includes(term)) {
          score += 25
        }
        
        // Bonus for multiple occurrences
        const occurrences = (lowerValue.match(new RegExp(term, 'g')) || []).length
        score += occurrences * 5
      }
    })

    return score
  }

  /**
   * Get database statistics
   */
  async getDatabaseStatistics(databaseId) {
    try {
      const db = this.registry.getActiveDatabase(databaseId)
      if (!db) {
        throw new Error(`Database '${databaseId}' is not connected`)
      }

      const dbInfo = await this.registry.getDatabaseInfo(databaseId)
      const stats = {
        database: databaseId,
        name: dbInfo.name,
        stores: {},
        totalRecords: 0,
        totalSize: 0
      }

      for (const storeName of Object.keys(dbInfo.stores)) {
        try {
          const tx = db.transaction(storeName, 'readonly')
          const store = tx.objectStore(storeName)
          const count = await store.count()
          
          stats.stores[storeName] = {
            recordCount: count,
            indexes: Object.keys(dbInfo.stores[storeName].indexes || {})
          }
          
          stats.totalRecords += count
          await tx.complete
        } catch (error) {
          console.warn(`Error getting stats for ${storeName}:`, error)
          stats.stores[storeName] = { recordCount: 0, indexes: [] }
        }
      }

      return stats
    } catch (error) {
      console.error('Error getting database statistics:', error)
      throw error
    }
  }

  /**
   * Export database data
   */
  async exportDatabase(databaseId, options = {}) {
    try {
      const { format = 'json', stores = null } = options
      
      const db = this.registry.getActiveDatabase(databaseId)
      if (!db) {
        throw new Error(`Database '${databaseId}' is not connected`)
      }

      const dbInfo = await this.registry.getDatabaseInfo(databaseId)
      const exportStores = stores || Object.keys(dbInfo.stores)
      
      const exportData = {
        metadata: {
          database: databaseId,
          name: dbInfo.name,
          exported: new Date().toISOString(),
          version: dbInfo.version
        },
        data: {}
      }

      for (const storeName of exportStores) {
        const storeData = await this.read(databaseId, storeName, { limit: 10000 })
        exportData.data[storeName] = storeData.data
      }

      if (format === 'json') {
        return JSON.stringify(exportData, null, 2)
      } else if (format === 'csv') {
        // Convert to CSV format (simplified)
        let csv = ''
        for (const [storeName, data] of Object.entries(exportData.data)) {
          csv += `\n\n=== ${storeName} ===\n`
          if (data.length > 0) {
            const headers = Object.keys(data[0])
            csv += headers.join(',') + '\n'
            data.forEach(row => {
              csv += headers.map(h => `"${(row[h] || '').toString().replace(/"/g, '""')}"`).join(',') + '\n'
            })
          }
        }
        return csv
      }

      return exportData
    } catch (error) {
      console.error('Error exporting database:', error)
      throw error
    }
  }

  /**
   * Import database data
   */
  async importDatabase(databaseId, importData, options = {}) {
    try {
      const { overwrite = false, storeName = null } = options
      
      const db = this.registry.getActiveDatabase(databaseId)
      if (!db) {
        throw new Error(`Database '${databaseId}' is not connected`)
      }

      let imported = 0
      const stores = storeName ? [storeName] : Object.keys(importData.data || {})

      for (const store of stores) {
        const data = importData.data[store]
        if (!data || !Array.isArray(data)) continue

        if (overwrite) {
          // Clear existing data
          const tx = db.transaction(store, 'readwrite')
          await tx.objectStore(store).clear()
          await tx.complete
        }

        // Import new data
        const results = await this.bulkCreate(databaseId, store, data)
        imported += results.length
      }

      console.log(`Imported ${imported} records into ${databaseId}`)
      return imported
    } catch (error) {
      console.error('Error importing database:', error)
      throw error
    }
  }
}

export default new DatabaseOperations()
