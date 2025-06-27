import { openDB } from 'idb'

/**
 * Database Registry Service
 * Manages multiple databases dynamically - add, remove, configure databases
 * Supports clipboard, browser history, bookmarks, and custom databases
 */
class DatabaseRegistry {
  constructor() {
    this.registryDbName = 'DatabaseRegistry'
    this.registryVersion = 1
    this.registryDb = null
    this.activeDatabases = new Map()
    
    // Default database templates
    this.databaseTemplates = {
      clipboard: {
        name: 'Clipboard Database',
        description: 'Stores clipboard history and content',
        stores: {
          clipboard_data: {
            keyPath: 'id',
            autoIncrement: true,
            indexes: [
              { name: 'timestamp', keyPath: 'timestamp' },
              { name: 'content_type', keyPath: 'content_type' },
              { name: 'size', keyPath: 'size_bytes' }
            ]
          }
        },
        category: 'system'
      },
      browser_history: {
        name: 'Browser History Database',
        description: 'Stores browser history and navigation data',
        stores: {
          history_data: {
            keyPath: 'id',
            autoIncrement: true,
            indexes: [
              { name: 'url', keyPath: 'url' },
              { name: 'title', keyPath: 'title' },
              { name: 'visitTime', keyPath: 'visitTime' },
              { name: 'visitCount', keyPath: 'visitCount' }
            ]
          }
        },
        category: 'browser'
      },
      bookmarks: {
        name: 'Bookmarks Database',
        description: 'Stores browser bookmarks and favorites',
        stores: {
          bookmark_data: {
            keyPath: 'id',
            autoIncrement: true,
            indexes: [
              { name: 'url', keyPath: 'url' },
              { name: 'title', keyPath: 'title' },
              { name: 'folder', keyPath: 'folder' },
              { name: 'dateAdded', keyPath: 'dateAdded' }
            ]
          }
        },
        category: 'browser'
      },
      notes: {
        name: 'Notes Database',
        description: 'Personal notes and text documents',
        stores: {
          notes_data: {
            keyPath: 'id',
            autoIncrement: true,
            indexes: [
              { name: 'title', keyPath: 'title' },
              { name: 'created', keyPath: 'created' },
              { name: 'modified', keyPath: 'modified' },
              { name: 'tags', keyPath: 'tags', multiEntry: true }
            ]
          }
        },
        category: 'personal'
      },
      contacts: {
        name: 'Contacts Database',
        description: 'Contact information and address book',
        stores: {
          contacts_data: {
            keyPath: 'id',
            autoIncrement: true,
            indexes: [
              { name: 'name', keyPath: 'name' },
              { name: 'email', keyPath: 'email' },
              { name: 'phone', keyPath: 'phone' },
              { name: 'company', keyPath: 'company' }
            ]
          }
        },
        category: 'personal'
      }
    }
  }

  /**
   * Initialize the database registry
   */
  async initializeRegistry() {
    try {
      this.registryDb = await openDB(this.registryDbName, this.registryVersion, {
        upgrade(db) {
          // Database registry store
          if (!db.objectStoreNames.contains('database_registry')) {
            const registryStore = db.createObjectStore('database_registry', {
              keyPath: 'id'
            })
            registryStore.createIndex('name', 'name')
            registryStore.createIndex('category', 'category')
            registryStore.createIndex('status', 'status')
            registryStore.createIndex('created', 'created')
          }

          // Database configurations store
          if (!db.objectStoreNames.contains('database_configs')) {
            const configStore = db.createObjectStore('database_configs', {
              keyPath: 'databaseId'
            })
            configStore.createIndex('type', 'type')
          }

          // Database relationships store
          if (!db.objectStoreNames.contains('database_relationships')) {
            const relationStore = db.createObjectStore('database_relationships', {
              keyPath: 'id',
              autoIncrement: true
            })
            relationStore.createIndex('sourceDb', 'sourceDb')
            relationStore.createIndex('targetDb', 'targetDb')
            relationStore.createIndex('relationshipType', 'relationshipType')
          }
        }
      })

      console.log('Database registry initialized successfully')
      await this.loadActiveDatabases()
      return true
    } catch (error) {
      console.error('Failed to initialize database registry:', error)
      return false
    }
  }

  /**
   * Add a new database
   */
  async addDatabase(config) {
    try {
      const {
        id,
        name,
        description = '',
        template = null,
        customStores = null,
        category = 'custom',
        autoConnect = true
      } = config

      // Validate required fields
      if (!id || !name) {
        throw new Error('Database ID and name are required')
      }

      // Check if database already exists
      const existing = await this.getDatabaseInfo(id)
      if (existing) {
        throw new Error(`Database with ID '${id}' already exists`)
      }

      // Determine database structure
      let stores = customStores
      if (template && this.databaseTemplates[template]) {
        stores = this.databaseTemplates[template].stores
      }

      if (!stores) {
        throw new Error('Database stores configuration is required')
      }

      // Create database entry
      const databaseEntry = {
        id,
        name,
        description,
        template,
        stores,
        category,
        status: 'inactive',
        created: new Date().toISOString(),
        modified: new Date().toISOString(),
        version: 1,
        size: 0,
        recordCount: 0
      }

      // Save to registry
      const tx = this.registryDb.transaction('database_registry', 'readwrite')
      await tx.objectStore('database_registry').add(databaseEntry)
      await tx.complete

      // Create the actual database if autoConnect is true
      if (autoConnect) {
        await this.connectDatabase(id)
      }

      console.log(`Database '${name}' added successfully`)
      return databaseEntry
    } catch (error) {
      console.error('Error adding database:', error)
      throw error
    }
  }

  /**
   * Remove a database
   */
  async removeDatabase(databaseId, options = {}) {
    try {
      const { deleteData = false, backup = true } = options

      // Get database info
      const dbInfo = await this.getDatabaseInfo(databaseId)
      if (!dbInfo) {
        throw new Error(`Database '${databaseId}' not found`)
      }

      // Create backup if requested
      if (backup && deleteData) {
        await this.backupDatabase(databaseId)
      }

      // Disconnect if connected
      if (this.activeDatabases.has(databaseId)) {
        await this.disconnectDatabase(databaseId)
      }

      // Delete actual database if requested
      if (deleteData) {
        await this.deleteActualDatabase(databaseId)
      }

      // Remove from registry
      const tx = this.registryDb.transaction(['database_registry', 'database_configs', 'database_relationships'], 'readwrite')
      
      await tx.objectStore('database_registry').delete(databaseId)
      await tx.objectStore('database_configs').delete(databaseId)
      
      // Remove relationships
      const relationshipStore = tx.objectStore('database_relationships')
      const sourceIndex = relationshipStore.index('sourceDb')
      const targetIndex = relationshipStore.index('targetDb')
      
      let cursor = await sourceIndex.openCursor(databaseId)
      while (cursor) {
        await cursor.delete()
        cursor = await cursor.continue()
      }
      
      cursor = await targetIndex.openCursor(databaseId)
      while (cursor) {
        await cursor.delete()
        cursor = await cursor.continue()
      }
      
      await tx.complete

      console.log(`Database '${dbInfo.name}' removed successfully`)
      return true
    } catch (error) {
      console.error('Error removing database:', error)
      throw error
    }
  }

  /**
   * Connect to a database
   */
  async connectDatabase(databaseId) {
    try {
      const dbInfo = await this.getDatabaseInfo(databaseId)
      if (!dbInfo) {
        throw new Error(`Database '${databaseId}' not found in registry`)
      }

      // Open the database
      const db = await openDB(databaseId, dbInfo.version, {
        upgrade(db, oldVersion, newVersion, transaction) {
          // Create stores based on configuration
          for (const [storeName, storeConfig] of Object.entries(dbInfo.stores)) {
            if (!db.objectStoreNames.contains(storeName)) {
              const store = db.createObjectStore(storeName, {
                keyPath: storeConfig.keyPath,
                autoIncrement: storeConfig.autoIncrement
              })

              // Create indexes
              if (storeConfig.indexes) {
                storeConfig.indexes.forEach(index => {
                  store.createIndex(index.name, index.keyPath, {
                    unique: index.unique || false,
                    multiEntry: index.multiEntry || false
                  })
                })
              }
            }
          }
        }
      })

      // Store active connection
      this.activeDatabases.set(databaseId, {
        db,
        info: dbInfo,
        connected: new Date().toISOString()
      })

      // Update status in registry
      await this.updateDatabaseStatus(databaseId, 'active')

      console.log(`Connected to database '${dbInfo.name}'`)
      return db
    } catch (error) {
      console.error('Error connecting to database:', error)
      throw error
    }
  }

  /**
   * Disconnect from a database
   */
  async disconnectDatabase(databaseId) {
    try {
      if (this.activeDatabases.has(databaseId)) {
        const connection = this.activeDatabases.get(databaseId)
        connection.db.close()
        this.activeDatabases.delete(databaseId)

        await this.updateDatabaseStatus(databaseId, 'inactive')
        console.log(`Disconnected from database '${databaseId}'`)
      }
      return true
    } catch (error) {
      console.error('Error disconnecting database:', error)
      throw error
    }
  }

  /**
   * Get database information
   */
  async getDatabaseInfo(databaseId) {
    try {
      const tx = this.registryDb.transaction('database_registry', 'readonly')
      const result = await tx.objectStore('database_registry').get(databaseId)
      await tx.complete
      return result
    } catch (error) {
      console.error('Error getting database info:', error)
      return null
    }
  }

  /**
   * List all registered databases
   */
  async listDatabases(options = {}) {
    try {
      const { category = null, status = null } = options
      
      const tx = this.registryDb.transaction('database_registry', 'readonly')
      const store = tx.objectStore('database_registry')
      
      let cursor
      if (category) {
        const index = store.index('category')
        cursor = await index.openCursor(category)
      } else if (status) {
        const index = store.index('status')
        cursor = await index.openCursor(status)
      } else {
        cursor = await store.openCursor()
      }

      const databases = []
      while (cursor) {
        databases.push(cursor.value)
        cursor = await cursor.continue()
      }

      await tx.complete
      return databases
    } catch (error) {
      console.error('Error listing databases:', error)
      return []
    }
  }

  /**
   * Update database status
   */
  async updateDatabaseStatus(databaseId, status) {
    try {
      const tx = this.registryDb.transaction('database_registry', 'readwrite')
      const store = tx.objectStore('database_registry')
      
      const dbInfo = await store.get(databaseId)
      if (dbInfo) {
        dbInfo.status = status
        dbInfo.modified = new Date().toISOString()
        await store.put(dbInfo)
      }
      
      await tx.complete
    } catch (error) {
      console.error('Error updating database status:', error)
    }
  }

  /**
   * Get active database connection
   */
  getActiveDatabase(databaseId) {
    const connection = this.activeDatabases.get(databaseId)
    return connection ? connection.db : null
  }

  /**
   * Load active databases on startup
   */
  async loadActiveDatabases() {
    try {
      const activeDbs = await this.listDatabases({ status: 'active' })
      for (const dbInfo of activeDbs) {
        try {
          await this.connectDatabase(dbInfo.id)
        } catch (error) {
          console.warn(`Failed to reconnect to database '${dbInfo.id}':`, error)
          await this.updateDatabaseStatus(dbInfo.id, 'inactive')
        }
      }
    } catch (error) {
      console.error('Error loading active databases:', error)
    }
  }

  /**
   * Backup database
   */
  async backupDatabase(databaseId) {
    try {
      const db = this.getActiveDatabase(databaseId)
      if (!db) {
        throw new Error(`Database '${databaseId}' is not connected`)
      }

      const dbInfo = await this.getDatabaseInfo(databaseId)
      const backup = {
        metadata: dbInfo,
        data: {},
        timestamp: new Date().toISOString()
      }

      // Export all stores
      for (const storeName of Object.keys(dbInfo.stores)) {
        const tx = db.transaction(storeName, 'readonly')
        const store = tx.objectStore(storeName)
        const cursor = await store.openCursor()
        
        backup.data[storeName] = []
        while (cursor) {
          backup.data[storeName].push(cursor.value)
          cursor = await cursor.continue()
        }
        await tx.complete
      }

      // Create backup file
      const blob = new Blob([JSON.stringify(backup, null, 2)], { 
        type: 'application/json' 
      })
      
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${databaseId}-backup-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      
      console.log(`Database '${databaseId}' backed up successfully`)
      return backup
    } catch (error) {
      console.error('Error backing up database:', error)
      throw error
    }
  }

  /**
   * Delete actual database
   */
  async deleteActualDatabase(databaseId) {
    try {
      // Close connection if open
      if (this.activeDatabases.has(databaseId)) {
        await this.disconnectDatabase(databaseId)
      }

      // Delete the IndexedDB database
      await new Promise((resolve, reject) => {
        const deleteReq = indexedDB.deleteDatabase(databaseId)
        deleteReq.onsuccess = () => resolve()
        deleteReq.onerror = () => reject(deleteReq.error)
        deleteReq.onblocked = () => {
          console.warn(`Database '${databaseId}' deletion blocked`)
          setTimeout(() => resolve(), 1000) // Continue anyway
        }
      })

      console.log(`Database '${databaseId}' deleted from IndexedDB`)
    } catch (error) {
      console.error('Error deleting actual database:', error)
      throw error
    }
  }

  /**
   * Get database templates
   */
  getDatabaseTemplates() {
    return this.databaseTemplates
  }

  /**
   * Add custom database template
   */
  addDatabaseTemplate(templateId, template) {
    this.databaseTemplates[templateId] = template
  }

  /**
   * Get database statistics
   */
  async getDatabaseStatistics() {
    try {
      const databases = await this.listDatabases()
      const stats = {
        total: databases.length,
        active: 0,
        inactive: 0,
        byCategory: {},
        totalSize: 0,
        totalRecords: 0
      }

      databases.forEach(db => {
        if (db.status === 'active') stats.active++
        else stats.inactive++

        stats.byCategory[db.category] = (stats.byCategory[db.category] || 0) + 1
        stats.totalSize += db.size || 0
        stats.totalRecords += db.recordCount || 0
      })

      return stats
    } catch (error) {
      console.error('Error getting database statistics:', error)
      return {}
    }
  }
}

export default new DatabaseRegistry()
