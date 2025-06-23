import neo4j from 'neo4j-driver'

/**
 * Neo4j Database Service for Clipboard Data
 * Provides graph database operations for clipboard content analysis
 */
class Neo4jService {
  constructor() {
    this.driver = null
    this.session = null
    this.isConnected = false
    
    // Default connection settings
    this.config = {
      uri: process.env.REACT_APP_NEO4J_URI || 'bolt://localhost:7687',
      username: process.env.REACT_APP_NEO4J_USERNAME || 'neo4j',
      password: process.env.REACT_APP_NEO4J_PASSWORD || 'password',
      database: process.env.REACT_APP_NEO4J_DATABASE || 'neo4j'
    }
  }

  /**
   * Initialize connection to Neo4j database
   */
  async connect() {
    try {
      this.driver = neo4j.driver(
        this.config.uri,
        neo4j.auth.basic(this.config.username, this.config.password),
        {
          disableLosslessIntegers: true,
          maxConnectionLifetime: 3 * 60 * 60 * 1000, // 3 hours
          maxConnectionPoolSize: 50,
          connectionAcquisitionTimeout: 2 * 60 * 1000, // 2 minutes
        }
      )

      // Test connection
      await this.driver.verifyConnectivity()
      this.isConnected = true
      console.log('Neo4j connection established')
      
      return true
    } catch (error) {
      console.error('Failed to connect to Neo4j:', error)
      this.isConnected = false
      return false
    }
  }

  /**
   * Close Neo4j connection
   */
  async disconnect() {
    if (this.session) {
      await this.session.close()
      this.session = null
    }
    
    if (this.driver) {
      await this.driver.close()
      this.driver = null
    }
    
    this.isConnected = false
    console.log('Neo4j connection closed')
  }

  /**
   * Get or create a new session
   */
  getSession() {
    if (!this.driver) {
      throw new Error('Neo4j driver not initialized. Call connect() first.')
    }
    
    return this.driver.session({ database: this.config.database })
  }

  /**
   * Store clipboard data in Neo4j graph format
   */
  async storeClipboardData(clipboardData) {
    const session = this.getSession()
    
    try {
      const tx = session.beginTransaction()
      
      // Create constraints and indexes
      await this.createConstraints(tx)
      
      for (const item of clipboardData) {
        await this.createClipboardNode(tx, item)
      }
      
      // Create relationships between clipboard items
      await this.createTemporalRelationships(tx, clipboardData)
      await this.createContentRelationships(tx, clipboardData)
      
      await tx.commit()
      console.log(`Stored ${clipboardData.length} clipboard items in Neo4j`)
      
    } catch (error) {
      console.error('Error storing clipboard data:', error)
      throw error
    } finally {
      await session.close()
    }
  }

  /**
   * Create database constraints and indexes
   */
  async createConstraints(tx) {
    const constraints = [
      'CREATE CONSTRAINT clipboard_id IF NOT EXISTS FOR (c:ClipboardItem) REQUIRE c.id IS UNIQUE',
      'CREATE CONSTRAINT content_type_name IF NOT EXISTS FOR (t:ContentType) REQUIRE t.name IS UNIQUE',
      'CREATE CONSTRAINT domain_name IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE',
      'CREATE CONSTRAINT keyword_text IF NOT EXISTS FOR (k:Keyword) REQUIRE k.text IS UNIQUE'
    ]
    
    for (const constraint of constraints) {
      try {
        await tx.run(constraint)
      } catch (error) {
        // Constraint might already exist, ignore error
        if (!error.message.includes('already exists')) {
          console.warn('Constraint creation warning:', error.message)
        }
      }
    }
  }

  /**
   * Create a clipboard item node with properties
   */
  async createClipboardNode(tx, item) {
    const contentType = this.getContentType(item.content)
    
    // Create clipboard item node
    await tx.run(`
      MERGE (c:ClipboardItem {id: $id})
      SET c.content = $content,
          c.contentType = $contentType,
          c.timestamp = datetime($timestamp),
          c.length = $length,
          c.preview = $preview
    `, {
      id: item.id || `item_${Date.now()}_${Math.random()}`,
      content: item.content,
      contentType: contentType,
      timestamp: item.timestamp,
      length: item.content.length,
      preview: item.content.substring(0, 100)
    })

    // Create content type node and relationship
    await tx.run(`
      MERGE (t:ContentType {name: $contentType})
      WITH t
      MATCH (c:ClipboardItem {id: $id})
      MERGE (c)-[:HAS_TYPE]->(t)
    `, {
      contentType: contentType,
      id: item.id || `item_${Date.now()}_${Math.random()}`
    })

    // Handle URL-specific processing
    if (contentType === 'URL') {
      const domain = this.extractDomain(item.content)
      if (domain) {
        await tx.run(`
          MERGE (d:Domain {name: $domain})
          WITH d
          MATCH (c:ClipboardItem {id: $id})
          MERGE (c)-[:FROM_DOMAIN]->(d)
        `, {
          domain: domain,
          id: item.id || `item_${Date.now()}_${Math.random()}`
        })
      }
    }

    // Extract and store keywords for text content
    if (contentType === 'Text') {
      const keywords = this.extractKeywords(item.content)
      for (const keyword of keywords.slice(0, 10)) { // Limit to top 10 keywords
        await tx.run(`
          MERGE (k:Keyword {text: $keyword})
          WITH k
          MATCH (c:ClipboardItem {id: $id})
          MERGE (c)-[:CONTAINS_KEYWORD {frequency: $frequency}]->(k)
        `, {
          keyword: keyword.text,
          frequency: keyword.frequency,
          id: item.id || `item_${Date.now()}_${Math.random()}`
        })
      }
    }
  }

  /**
   * Create temporal relationships between clipboard items
   */
  async createTemporalRelationships(tx, clipboardData) {
    for (let i = 1; i < clipboardData.length; i++) {
      const current = clipboardData[i]
      const previous = clipboardData[i - 1]
      
      const timeDiff = new Date(current.timestamp) - new Date(previous.timestamp)
      const maxTimeDiff = 5 * 60 * 1000 // 5 minutes
      
      if (timeDiff <= maxTimeDiff) {
        await tx.run(`
          MATCH (prev:ClipboardItem {id: $prevId})
          MATCH (curr:ClipboardItem {id: $currId})
          MERGE (prev)-[:FOLLOWED_BY {timeDiff: $timeDiff}]->(curr)
        `, {
          prevId: previous.id || `item_${i-1}`,
          currId: current.id || `item_${i}`,
          timeDiff: timeDiff
        })
      }
    }
  }

  /**
   * Create content-based relationships
   */
  async createContentRelationships(tx, clipboardData) {
    // Create similarity relationships for similar content
    for (let i = 0; i < clipboardData.length; i++) {
      for (let j = i + 1; j < clipboardData.length; j++) {
        const similarity = this.calculateContentSimilarity(
          clipboardData[i].content,
          clipboardData[j].content
        )
        
        if (similarity > 0.7) { // High similarity threshold
          await tx.run(`
            MATCH (item1:ClipboardItem {id: $id1})
            MATCH (item2:ClipboardItem {id: $id2})
            MERGE (item1)-[:SIMILAR_TO {similarity: $similarity}]->(item2)
          `, {
            id1: clipboardData[i].id || `item_${i}`,
            id2: clipboardData[j].id || `item_${j}`,
            similarity: similarity
          })
        }
      }
    }
  }

  /**
   * Query clipboard data for visualization
   */
  async getClipboardGraph(limit = 50) {
    const session = this.getSession()
    
    try {
      const result = await session.run(`
        MATCH (c:ClipboardItem)
        OPTIONAL MATCH (c)-[r]->(related)
        RETURN c, r, related
        ORDER BY c.timestamp DESC
        LIMIT $limit
      `, { limit: neo4j.int(limit) })

      return this.processGraphResult(result)
      
    } catch (error) {
      console.error('Error querying clipboard graph:', error)
      throw error
    } finally {
      await session.close()
    }
  }

  /**
   * Get content type statistics
   */
  async getContentTypeStats() {
    const session = this.getSession()
    
    try {
      const result = await session.run(`
        MATCH (c:ClipboardItem)-[:HAS_TYPE]->(t:ContentType)
        RETURN t.name as contentType, count(c) as count
        ORDER BY count DESC
      `)

      return result.records.map(record => ({
        type: record.get('contentType'),
        count: record.get('count').toNumber()
      }))
      
    } catch (error) {
      console.error('Error getting content type stats:', error)
      throw error
    } finally {
      await session.close()
    }
  }

  /**
   * Process Neo4j query result into D3.js format
   */
  processGraphResult(result) {
    const nodes = new Map()
    const links = []

    result.records.forEach(record => {
      const clipboardItem = record.get('c')
      const relationship = record.get('r')
      const relatedNode = record.get('related')

      // Add clipboard item node
      if (clipboardItem && !nodes.has(clipboardItem.identity.toString())) {
        nodes.set(clipboardItem.identity.toString(), {
          id: clipboardItem.identity.toString(),
          label: clipboardItem.properties.preview || 'Clipboard Item',
          type: 'clipboard',
          properties: clipboardItem.properties
        })
      }

      // Add related node and relationship
      if (relatedNode && relationship) {
        const relatedId = relatedNode.identity.toString()
        
        if (!nodes.has(relatedId)) {
          nodes.set(relatedId, {
            id: relatedId,
            label: relatedNode.properties.name || relatedNode.properties.text || 'Related',
            type: relatedNode.labels[0].toLowerCase(),
            properties: relatedNode.properties
          })
        }

        links.push({
          source: clipboardItem.identity.toString(),
          target: relatedId,
          relationship: relationship.type,
          properties: relationship.properties
        })
      }
    })

    return {
      nodes: Array.from(nodes.values()),
      links: links
    }
  }

  /**
   * Utility methods
   */
  getContentType(content) {
    if (content.trim().startsWith('{') || content.trim().startsWith('[')) return 'JSON'
    if (content.includes('http://') || content.includes('https://')) return 'URL'
    if (content.includes(',') && content.includes('\n')) return 'CSV'
    if (content.includes('@') && content.includes('.')) return 'Email'
    return 'Text'
  }

  extractDomain(url) {
    try {
      return new URL(url).hostname
    } catch {
      return null
    }
  }

  extractKeywords(text) {
    const words = text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 3)
    
    const freq = {}
    words.forEach(word => {
      freq[word] = (freq[word] || 0) + 1
    })
    
    return Object.entries(freq)
      .map(([text, frequency]) => ({ text, frequency }))
      .sort((a, b) => b.frequency - a.frequency)
  }

  calculateContentSimilarity(content1, content2) {
    // Simple Jaccard similarity
    const words1 = new Set(content1.toLowerCase().split(/\s+/))
    const words2 = new Set(content2.toLowerCase().split(/\s+/))
    
    const intersection = new Set([...words1].filter(x => words2.has(x)))
    const union = new Set([...words1, ...words2])
    
    return intersection.size / union.size
  }
}

export default new Neo4jService()
