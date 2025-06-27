import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material'
import {
  Storage,
  ContentPaste,
  History,
  BookmarkBorder,
  Note,
  Contacts,
  CheckCircle,
  PlayArrow,
  Settings,
  DataObject
} from '@mui/icons-material'
import DatabaseRegistry from '../services/DatabaseRegistry'
import DatabaseOperations from '../services/DatabaseOperations'

function QuickDatabaseSetup({ onComplete }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [setupProgress, setSetupProgress] = useState(0)
  const [selectedDatabases, setSelectedDatabases] = useState([])
  const [setupDialog, setSetupDialog] = useState(false)

  const databaseTemplates = [
    {
      id: 'clipboard',
      name: 'Clipboard Database',
      description: 'Store and manage clipboard history with intelligent categorization',
      icon: <ContentPaste />,
      category: 'system',
      essential: true,
      features: ['Content history', 'Type detection', 'Search & filter', 'Export capabilities']
    },
    {
      id: 'browser_history',
      name: 'Browser History',
      description: 'Import and analyze browser history from multiple browsers',
      icon: <History />,
      category: 'browser',
      essential: true,
      features: ['Multi-browser support', 'Visit tracking', 'URL analysis', 'Timeline view']
    },
    {
      id: 'bookmarks',
      name: 'Bookmarks Database',
      description: 'Organize and manage bookmarks from various browsers',
      icon: <BookmarkBorder />,
      category: 'browser',
      essential: false,
      features: ['Folder organization', 'Tag system', 'Duplicate detection', 'Import/export']
    },
    {
      id: 'notes',
      name: 'Notes Database',
      description: 'Personal notes and text documents with full-text search',
      icon: <Note />,
      category: 'personal',
      essential: false,
      features: ['Rich text support', 'Tag system', 'Full-text search', 'Version history']
    },
    {
      id: 'contacts',
      name: 'Contacts Database',
      description: 'Contact information and address book management',
      icon: <Contacts />,
      category: 'personal',
      essential: false,
      features: ['Contact details', 'Company info', 'Search & filter', 'Export formats']
    }
  ]

  const setupSteps = [
    'Initialize Database Registry',
    'Create Selected Databases',
    'Configure Database Settings',
    'Populate Sample Data',
    'Verify Connections'
  ]

  const handleDatabaseToggle = (templateId) => {
    setSelectedDatabases(prev => {
      if (prev.includes(templateId)) {
        return prev.filter(id => id !== templateId)
      } else {
        return [...prev, templateId]
      }
    })
  }

  const handleQuickSetup = () => {
    // Select essential databases by default
    const essentialDbs = databaseTemplates
      .filter(template => template.essential)
      .map(template => template.id)
    
    setSelectedDatabases(essentialDbs)
    setSetupDialog(true)
  }

  const handleCustomSetup = () => {
    setSetupDialog(true)
  }

  const executeSetup = async () => {
    setLoading(true)
    setError(null)
    setSetupProgress(0)

    try {
      // Step 1: Initialize Database Registry
      setSetupProgress(1)
      await DatabaseRegistry.initializeRegistry()
      await DatabaseOperations.initialize()

      // Step 2: Create Selected Databases
      setSetupProgress(2)
      const createdDatabases = []

      for (const templateId of selectedDatabases) {
        const template = databaseTemplates.find(t => t.id === templateId)
        if (template) {
          const databaseConfig = {
            id: `${templateId}_${Date.now()}`,
            name: template.name,
            description: template.description,
            template: templateId,
            category: template.category,
            autoConnect: true
          }

          const database = await DatabaseRegistry.addDatabase(databaseConfig)
          createdDatabases.push(database)
        }
      }

      // Step 3: Configure Database Settings
      setSetupProgress(3)
      // Configuration is handled automatically by templates

      // Step 4: Populate Sample Data
      setSetupProgress(4)
      for (const database of createdDatabases) {
        await populateSampleData(database)
      }

      // Step 5: Verify Connections
      setSetupProgress(5)
      const stats = await DatabaseRegistry.getDatabaseStatistics()

      setSuccess(`Successfully set up ${createdDatabases.length} databases with ${stats.totalRecords} sample records`)
      setSetupDialog(false)
      
      if (onComplete) {
        onComplete(createdDatabases)
      }
    } catch (err) {
      setError('Setup failed: ' + err.message)
    } finally {
      setLoading(false)
      setSetupProgress(0)
    }
  }

  const populateSampleData = async (database) => {
    try {
      const db = DatabaseRegistry.getActiveDatabase(database.id)
      if (!db) return

      switch (database.template) {
        case 'clipboard':
          await populateClipboardSamples(database.id)
          break
        case 'browser_history':
          await populateBrowserHistorySamples(database.id)
          break
        case 'bookmarks':
          await populateBookmarkSamples(database.id)
          break
        case 'notes':
          await populateNotesSamples(database.id)
          break
        case 'contacts':
          await populateContactsSamples(database.id)
          break
      }
    } catch (error) {
      console.warn(`Failed to populate sample data for ${database.id}:`, error)
    }
  }

  const populateClipboardSamples = async (databaseId) => {
    const samples = [
      {
        content: 'https://github.com/user/repository',
        content_type: 'URL',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        size_bytes: 32,
        source: 'sample'
      },
      {
        content: 'Important meeting notes from today',
        content_type: 'Text',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        size_bytes: 32,
        source: 'sample'
      },
      {
        content: '{"name": "John", "age": 30}',
        content_type: 'JSON',
        timestamp: new Date(Date.now() - 10800000).toISOString(),
        size_bytes: 25,
        source: 'sample'
      }
    ]

    await DatabaseOperations.bulkCreate(databaseId, 'clipboard_data', samples)
  }

  const populateBrowserHistorySamples = async (databaseId) => {
    const samples = [
      {
        url: 'https://github.com',
        title: 'GitHub',
        visitTime: new Date(Date.now() - 3600000).toISOString(),
        visitCount: 5,
        source: 'sample'
      },
      {
        url: 'https://stackoverflow.com',
        title: 'Stack Overflow',
        visitTime: new Date(Date.now() - 7200000).toISOString(),
        visitCount: 12,
        source: 'sample'
      }
    ]

    await DatabaseOperations.bulkCreate(databaseId, 'history_data', samples)
  }

  const populateBookmarkSamples = async (databaseId) => {
    const samples = [
      {
        url: 'https://developer.mozilla.org',
        title: 'MDN Web Docs',
        folder: 'Development',
        dateAdded: new Date().toISOString(),
        source: 'sample'
      },
      {
        url: 'https://reactjs.org',
        title: 'React Documentation',
        folder: 'Development/React',
        dateAdded: new Date().toISOString(),
        source: 'sample'
      }
    ]

    await DatabaseOperations.bulkCreate(databaseId, 'bookmark_data', samples)
  }

  const populateNotesSamples = async (databaseId) => {
    const samples = [
      {
        title: 'Project Ideas',
        content: 'List of potential project ideas for next quarter',
        tags: ['projects', 'planning'],
        created: new Date().toISOString(),
        source: 'sample'
      },
      {
        title: 'Meeting Notes',
        content: 'Notes from the team meeting on database architecture',
        tags: ['meetings', 'database'],
        created: new Date().toISOString(),
        source: 'sample'
      }
    ]

    await DatabaseOperations.bulkCreate(databaseId, 'notes_data', samples)
  }

  const populateContactsSamples = async (databaseId) => {
    const samples = [
      {
        name: 'John Doe',
        email: 'john.doe@example.com',
        phone: '+1-555-0123',
        company: 'Tech Corp',
        source: 'sample'
      },
      {
        name: 'Jane Smith',
        email: 'jane.smith@example.com',
        phone: '+1-555-0456',
        company: 'Design Studio',
        source: 'sample'
      }
    ]

    await DatabaseOperations.bulkCreate(databaseId, 'contacts_data', samples)
  }

  const DatabaseTemplateCard = ({ template }) => (
    <Card 
      sx={{ 
        height: '100%',
        border: selectedDatabases.includes(template.id) ? 2 : 1,
        borderColor: selectedDatabases.includes(template.id) ? 'primary.main' : 'divider',
        cursor: 'pointer'
      }}
      onClick={() => handleDatabaseToggle(template.id)}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {template.icon}
            <Typography variant="h6" component="div">
              {template.name}
            </Typography>
          </Box>
          {template.essential && (
            <Chip label="Essential" size="small" color="primary" />
          )}
        </Box>
        
        <Typography variant="body2" color="text.secondary" paragraph>
          {template.description}
        </Typography>
        
        <Typography variant="subtitle2" gutterBottom>
          Features:
        </Typography>
        <List dense>
          {template.features.map((feature, index) => (
            <ListItem key={index} sx={{ py: 0, px: 0 }}>
              <ListItemIcon sx={{ minWidth: 20 }}>
                <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
              </ListItemIcon>
              <ListItemText 
                primary={feature} 
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  )

  return (
    <Box>
      {/* Status Messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Loading Progress */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Quick Setup Options */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          <Storage sx={{ mr: 1, verticalAlign: 'middle' }} />
          Quick Database Setup
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Get started quickly with pre-configured databases for common use cases.
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Button
              variant="contained"
              size="large"
              startIcon={<PlayArrow />}
              onClick={handleQuickSetup}
              fullWidth
            >
              Quick Setup (Essential Databases)
            </Button>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Sets up clipboard and browser history databases with sample data
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Button
              variant="outlined"
              size="large"
              startIcon={<Settings />}
              onClick={handleCustomSetup}
              fullWidth
            >
              Custom Setup
            </Button>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Choose which databases to create and configure
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Database Templates */}
      <Typography variant="h6" gutterBottom>
        Available Database Templates
      </Typography>
      <Grid container spacing={3}>
        {databaseTemplates.map((template) => (
          <Grid item xs={12} md={6} lg={4} key={template.id}>
            <DatabaseTemplateCard template={template} />
          </Grid>
        ))}
      </Grid>

      {/* Setup Dialog */}
      <Dialog open={setupDialog} onClose={() => setSetupDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Database Setup</DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Setting up {selectedDatabases.length} database(s) with sample data.
          </Typography>
          
          {loading && (
            <Box sx={{ mb: 2 }}>
              <Stepper activeStep={setupProgress - 1} orientation="vertical">
                {setupSteps.map((step, index) => (
                  <Step key={step}>
                    <StepLabel>{step}</StepLabel>
                    <StepContent>
                      <Typography variant="body2" color="text.secondary">
                        {index === setupProgress - 1 ? 'In progress...' : 'Completed'}
                      </Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </Box>
          )}

          <Typography variant="subtitle2" gutterBottom>
            Selected Databases:
          </Typography>
          <List>
            {selectedDatabases.map(templateId => {
              const template = databaseTemplates.find(t => t.id === templateId)
              return template ? (
                <ListItem key={templateId}>
                  <ListItemIcon>{template.icon}</ListItemIcon>
                  <ListItemText 
                    primary={template.name}
                    secondary={template.description}
                  />
                </ListItem>
              ) : null
            })}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSetupDialog(false)} disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={executeSetup} 
            variant="contained"
            disabled={loading || selectedDatabases.length === 0}
          >
            {loading ? 'Setting up...' : 'Start Setup'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default QuickDatabaseSetup
