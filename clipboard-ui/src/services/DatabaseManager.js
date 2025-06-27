import { openDB } from 'idb'

/**
 * Comprehensive Database Management Service
 * Handles CRUD operations for clipboard, bookmarks, and browser history data
 */
class DatabaseManager {
  constructor() {
    this.dbName = 'ClipboardIntelligenceDB'
    this.version = 1
    this.db = null
    this.stores = {
      clipboard: 'clipboard_data',
      bookmarks: 'bookmark_data', 
      history: 'browser_history',
      merged: 'merged_data',
      metadata: 'database_metadata'
    }
  }

  /**
   * Initialize the database with all required object stores
   */
  async initializeDatabase() {
    try {
      this.db = await openDB(this.dbName, this.version, {
        upgrade(db) {
          // Clipboard data store
          if (!db.objectStoreNames.contains('clipboard_data')) {
            const clipboardStore = db.createObjectStore('clipboard_data', {
              keyPath: 'id',
              autoIncrement: true
            })
            clipboardStore.createIndex('timestamp', 'timestamp')
            clipboardStore.createIndex('content_type', 'content_type')
            clipboardStore.createIndex('size', 'size_bytes')
          }

          // Bookmark data store
          if (!db.objectStoreNames.contains('bookmark_data')) {
            const bookmarkStore = db.createObjectStore('bookmark_data', {
              keyPath: 'id',
              autoIncrement: true
            })
            bookmarkStore.createIndex('url', 'url')
            bookmarkStore.createIndex('title', 'title')
            bookmarkStore.createIndex('folder', 'folder')
            bookmarkStore.createIndex('dateAdded', 'dateAdded')
          }

          // Browser history store
          if (!db.objectStoreNames.contains('browser_history')) {
            const historyStore = db.createObjectStore('browser_history', {
              keyPath: 'id',
              autoIncrement: true
            })
            historyStore.createIndex('url', 'url')
            historyStore.createIndex('title', 'title')
            historyStore.createIndex('visitTime', 'visitTime')
            historyStore.createIndex('visitCount', 'visitCount')
          }

          // Merged data store for combined analysis
          if (!db.objectStoreNames.contains('merged_data')) {
            const mergedStore = db.createObjectStore('merged_data', {
              keyPath: 'id',
              autoIncrement: true
            })
            mergedStore.createIndex('source', 'source') // clipboard, bookmark, history
            mergedStore.createIndex('timestamp', 'timestamp')
            mergedStore.createIndex('content_type', 'content_type')
          }

          // Metadata store for database information
          if (!db.objectStoreNames.contains('database_metadata')) {
            const metadataStore = db.createObjectStore('database_metadata', {
              keyPath: 'key'
            })
          }
        }
      })

      console.log('Database initialized successfully')
      await this.updateMetadata('last_initialized', new Date().toISOString())
      return true
    } catch (error) {
      console.error('Failed to initialize database:', error)
      return false
    }
  }

  /**
   * CLIPBOARD DATA OPERATIONS
   */

  // Create clipboard entry
  async createClipboardEntry(data) {
    try {
      const entry = {
        content: data.content,
        content_type: data.content_type || this.detectContentType(data.content),
        timestamp: data.timestamp || new Date().toISOString(),
        size_bytes: data.content.length,
        source: 'clipboard',
        metadata: {
          word_count: data.content.split(/\s+/).length,
          char_count: data.content.length,
          created_at: new Date().toISOString()
        }
      }

      const result = await this.db.add(this.stores.clipboard, entry)
      console.log('Clipboard entry created:', result)
      return result
    } catch (error) {
      console.error('Error creating clipboard entry:', error)
      throw error
    }
  }

  // Read clipboard entries with filtering and pagination
  async readClipboardEntries(options = {}) {
    try {
      const {
        limit = 100,
        offset = 0,
        contentType = null,
        startDate = null,
        endDate = null,
        searchTerm = null
      } = options

      const tx = this.db.transaction(this.stores.clipboard, 'readonly')
      const store = tx.objectStore(this.stores.clipboard)
      
      let cursor
      if (contentType) {
        const index = store.index('content_type')
        cursor = await index.openCursor(contentType)
      } else {
        cursor = await store.openCursor()
      }

      const results = []
      let count = 0
      let skipped = 0

      while (cursor && results.length < limit) {
        const entry = cursor.value

        // Apply filters
        let include = true

        if (startDate && new Date(entry.timestamp) < new Date(startDate)) {
          include = false
        }
        if (endDate && new Date(entry.timestamp) > new Date(endDate)) {
          include = false
        }
        if (searchTerm && !entry.content.toLowerCase().includes(searchTerm.toLowerCase())) {
          include = false
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

      return {
        data: results,
        total: count,
        hasMore: cursor !== null
      }
    } catch (error) {
      console.error('Error reading clipboard entries:', error)
      throw error
    }
  }

  // Update clipboard entry
  async updateClipboardEntry(id, updates) {
    try {
      const tx = this.db.transaction(this.stores.clipboard, 'readwrite')
      const store = tx.objectStore(this.stores.clipboard)
      
      const existing = await store.get(id)
      if (!existing) {
        throw new Error(`Clipboard entry with id ${id} not found`)
      }

      const updated = {
        ...existing,
        ...updates,
        metadata: {
          ...existing.metadata,
          ...updates.metadata,
          updated_at: new Date().toISOString()
        }
      }

      await store.put(updated)
      await tx.complete
      
      console.log('Clipboard entry updated:', id)
      return updated
    } catch (error) {
      console.error('Error updating clipboard entry:', error)
      throw error
    }
  }

  // Delete clipboard entry
  async deleteClipboardEntry(id) {
    try {
      const tx = this.db.transaction(this.stores.clipboard, 'readwrite')
      await tx.objectStore(this.stores.clipboard).delete(id)
      await tx.complete
      
      console.log('Clipboard entry deleted:', id)
      return true
    } catch (error) {
      console.error('Error deleting clipboard entry:', error)
      throw error
    }
  }

  // Bulk delete clipboard entries
  async bulkDeleteClipboardEntries(ids) {
    try {
      const tx = this.db.transaction(this.stores.clipboard, 'readwrite')
      const store = tx.objectStore(this.stores.clipboard)
      
      for (const id of ids) {
        await store.delete(id)
      }
      
      await tx.complete
      console.log(`Bulk deleted ${ids.length} clipboard entries`)
      return true
    } catch (error) {
      console.error('Error bulk deleting clipboard entries:', error)
      throw error
    }
  }

  /**
   * BROWSER BOOKMARK OPERATIONS
   */

  // Import browser bookmarks
  async importBookmarks(bookmarkData) {
    try {
      const tx = this.db.transaction(this.stores.bookmarks, 'readwrite')
      const store = tx.objectStore(this.stores.bookmarks)
      
      let imported = 0
      for (const bookmark of bookmarkData) {
        const entry = {
          url: bookmark.url,
          title: bookmark.title || bookmark.url,
          folder: bookmark.folder || 'Imported',
          dateAdded: bookmark.dateAdded || new Date().toISOString(),
          source: 'browser_import',
          metadata: {
            imported_at: new Date().toISOString(),
            original_id: bookmark.id
          }
        }
        
        await store.add(entry)
        imported++
      }
      
      await tx.complete
      console.log(`Imported ${imported} bookmarks`)
      return imported
    } catch (error) {
      console.error('Error importing bookmarks:', error)
      throw error
    }
  }

  // Read bookmarks with filtering
  async readBookmarks(options = {}) {
    try {
      const {
        limit = 100,
        folder = null,
        searchTerm = null
      } = options

      const tx = this.db.transaction(this.stores.bookmarks, 'readonly')
      const store = tx.objectStore(this.stores.bookmarks)
      
      let cursor
      if (folder) {
        const index = store.index('folder')
        cursor = await index.openCursor(folder)
      } else {
        cursor = await store.openCursor()
      }

      const results = []
      while (cursor && results.length < limit) {
        const entry = cursor.value

        if (!searchTerm || 
            entry.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            entry.url.toLowerCase().includes(searchTerm.toLowerCase())) {
          results.push(entry)
        }

        cursor = await cursor.continue()
      }

      return results
    } catch (error) {
      console.error('Error reading bookmarks:', error)
      throw error
    }
  }

  /**
   * BROWSER HISTORY OPERATIONS
   */

  // Import browser history
  async importBrowserHistory(historyData) {
    try {
      const tx = this.db.transaction(this.stores.history, 'readwrite')
      const store = tx.objectStore(this.stores.history)
      
      let imported = 0
      for (const historyItem of historyData) {
        const entry = {
          url: historyItem.url,
          title: historyItem.title || historyItem.url,
          visitTime: historyItem.visitTime || historyItem.lastVisitTime,
          visitCount: historyItem.visitCount || 1,
          source: 'browser_import',
          metadata: {
            imported_at: new Date().toISOString(),
            original_id: historyItem.id
          }
        }
        
        await store.add(entry)
        imported++
      }
      
      await tx.complete
      console.log(`Imported ${imported} history items`)
      return imported
    } catch (error) {
      console.error('Error importing browser history:', error)
      throw error
    }
  }

  /**
   * MERGE AND ANALYSIS OPERATIONS
   */

  // Merge data from different sources for unified analysis
  async mergeDataSources(options = {}) {
    try {
      const { includeClipboard = true, includeBookmarks = true, includeHistory = true } = options
      
      const tx = this.db.transaction([this.stores.clipboard, this.stores.bookmarks, this.stores.history, this.stores.merged], 'readwrite')
      const mergedStore = tx.objectStore(this.stores.merged)
      
      // Clear existing merged data
      await mergedStore.clear()
      
      let merged = 0

      // Merge clipboard data
      if (includeClipboard) {
        const clipboardData = await this.readClipboardEntries({ limit: 1000 })
        for (const item of clipboardData.data) {
          await mergedStore.add({
            ...item,
            source: 'clipboard',
            unified_content: item.content,
            unified_timestamp: item.timestamp
          })
          merged++
        }
      }

      // Merge bookmark data
      if (includeBookmarks) {
        const bookmarks = await this.readBookmarks({ limit: 1000 })
        for (const item of bookmarks) {
          await mergedStore.add({
            ...item,
            source: 'bookmark',
            unified_content: `${item.title} - ${item.url}`,
            unified_timestamp: item.dateAdded,
            content_type: 'URL'
          })
          merged++
        }
      }

      // Merge history data
      if (includeHistory) {
        const historyTx = this.db.transaction(this.stores.history, 'readonly')
        const historyStore = historyTx.objectStore(this.stores.history)
        const historyCursor = await historyStore.openCursor()
        
        while (historyCursor) {
          const item = historyCursor.value
          await mergedStore.add({
            ...item,
            source: 'history',
            unified_content: `${item.title} - ${item.url}`,
            unified_timestamp: item.visitTime,
            content_type: 'URL'
          })
          merged++
          historyCursor = await historyCursor.continue()
        }
      }

      await tx.complete
      console.log(`Merged ${merged} items from different sources`)
      return merged
    } catch (error) {
      console.error('Error merging data sources:', error)
      throw error
    }
  }

  // Get merged data for analysis
  async getMergedData(options = {}) {
    try {
      const { limit = 100, source = null } = options
      
      const tx = this.db.transaction(this.stores.merged, 'readonly')
      const store = tx.objectStore(this.stores.merged)
      
      let cursor
      if (source) {
        const index = store.index('source')
        cursor = await index.openCursor(source)
      } else {
        cursor = await store.openCursor()
      }

      const results = []
      while (cursor && results.length < limit) {
        results.push(cursor.value)
        cursor = await cursor.continue()
      }

      return results
    } catch (error) {
      console.error('Error getting merged data:', error)
      throw error
    }
  }

  /**
   * UTILITY METHODS
   */

  // Detect content type
  detectContentType(content) {
    if (content.trim().startsWith('{') || content.trim().startsWith('[')) return 'JSON'
    if (content.includes('http://') || content.includes('https://')) return 'URL'
    if (content.includes(',') && content.includes('\n')) return 'CSV'
    if (content.includes('@') && content.includes('.')) return 'Email'
    return 'Text'
  }

  // Update metadata
  async updateMetadata(key, value) {
    try {
      const tx = this.db.transaction(this.stores.metadata, 'readwrite')
      await tx.objectStore(this.stores.metadata).put({ key, value, updated_at: new Date().toISOString() })
      await tx.complete
    } catch (error) {
      console.error('Error updating metadata:', error)
    }
  }

  // Get database statistics
  async getDatabaseStats() {
    try {
      const stats = {}
      
      for (const [name, storeName] of Object.entries(this.stores)) {
        if (name === 'metadata') continue
        
        const tx = this.db.transaction(storeName, 'readonly')
        const store = tx.objectStore(storeName)
        const count = await store.count()
        stats[name] = count
      }

      return stats
    } catch (error) {
      console.error('Error getting database stats:', error)
      return {}
    }
  }

  // Export data for backup
  async exportData(storeName = null) {
    try {
      const exports = {}
      const storesToExport = storeName ? [storeName] : Object.values(this.stores)
      
      for (const store of storesToExport) {
        const tx = this.db.transaction(store, 'readonly')
        const cursor = await tx.objectStore(store).openCursor()
        const data = []
        
        while (cursor) {
          data.push(cursor.value)
          cursor = await cursor.continue()
        }
        
        exports[store] = data
      }

      return exports
    } catch (error) {
      console.error('Error exporting data:', error)
      throw error
    }
  }

  // Clear all data
  async clearAllData() {
    try {
      for (const storeName of Object.values(this.stores)) {
        const tx = this.db.transaction(storeName, 'readwrite')
        await tx.objectStore(storeName).clear()
        await tx.complete
      }
      
      console.log('All data cleared')
      return true
    } catch (error) {
      console.error('Error clearing data:', error)
      throw error
    }
  }
}

export default new DatabaseManager()
