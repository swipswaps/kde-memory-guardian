import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  Tooltip,
  Badge
} from '@mui/material'
import {
  Add,
  Delete,
  Edit,
  Storage,
  CloudUpload,
  CloudDownload,
  Refresh,
  Info,
  Warning,
  CheckCircle,
  Error,
  ExpandMore,
  BookmarkBorder,
  History,
  ContentPaste,
  DataObject,
  Backup,
  Restore,
  Link,
  LinkOff,
  Visibility,
  VisibilityOff,
  Settings,
  Category,
  Timeline,
  Assessment
} from '@mui/icons-material'
import DatabaseRegistry from '../services/DatabaseRegistry'

function DatabaseManagementPanel() {
  const [databases, setDatabases] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [statistics, setStatistics] = useState({})

  // Dialog states
  const [addDialog, setAddDialog] = useState(false)
  const [removeDialog, setRemoveDialog] = useState(false)
  const [selectedDatabase, setSelectedDatabase] = useState(null)

  // Add database form state
  const [newDatabase, setNewDatabase] = useState({
    id: '',
    name: '',
    description: '',
    template: '',
    category: 'custom',
    autoConnect: true
  })

  // Remove database options
  const [removeOptions, setRemoveOptions] = useState({
    deleteData: false,
    backup: true
  })

  useEffect(() => {
    initializeAndLoadDatabases()
  }, [])

  const initializeAndLoadDatabases = async () => {
    setLoading(true)
    try {
      await DatabaseRegistry.initializeRegistry()
      await loadDatabases()
      await loadStatistics()
      setSuccess('Database registry initialized successfully')
    } catch (err) {
      setError('Failed to initialize database registry: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadDatabases = async () => {
    try {
      const dbList = await DatabaseRegistry.listDatabases()
      setDatabases(dbList)
    } catch (err) {
      setError('Failed to load databases: ' + err.message)
    }
  }

  const loadStatistics = async () => {
    try {
      const stats = await DatabaseRegistry.getDatabaseStatistics()
      setStatistics(stats)
    } catch (err) {
      console.error('Failed to load statistics:', err)
    }
  }

  const handleAddDatabase = async () => {
    if (!newDatabase.id || !newDatabase.name) {
      setError('Database ID and name are required')
      return
    }

    setLoading(true)
    try {
      await DatabaseRegistry.addDatabase(newDatabase)
      await loadDatabases()
      await loadStatistics()
      setSuccess(`Database '${newDatabase.name}' added successfully`)
      setAddDialog(false)
      setNewDatabase({
        id: '',
        name: '',
        description: '',
        template: '',
        category: 'custom',
        autoConnect: true
      })
    } catch (err) {
      setError('Failed to add database: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveDatabase = async () => {
    if (!selectedDatabase) return

    setLoading(true)
    try {
      await DatabaseRegistry.removeDatabase(selectedDatabase.id, removeOptions)
      await loadDatabases()
      await loadStatistics()
      setSuccess(`Database '${selectedDatabase.name}' removed successfully`)
      setRemoveDialog(false)
      setSelectedDatabase(null)
    } catch (err) {
      setError('Failed to remove database: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleConnectDatabase = async (databaseId) => {
    setLoading(true)
    try {
      await DatabaseRegistry.connectDatabase(databaseId)
      await loadDatabases()
      setSuccess(`Connected to database successfully`)
    } catch (err) {
      setError('Failed to connect to database: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDisconnectDatabase = async (databaseId) => {
    setLoading(true)
    try {
      await DatabaseRegistry.disconnectDatabase(databaseId)
      await loadDatabases()
      setSuccess(`Disconnected from database successfully`)
    } catch (err) {
      setError('Failed to disconnect from database: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleBackupDatabase = async (databaseId) => {
    setLoading(true)
    try {
      await DatabaseRegistry.backupDatabase(databaseId)
      setSuccess(`Database backup created successfully`)
    } catch (err) {
      setError('Failed to backup database: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success'
      case 'inactive': return 'default'
      case 'error': return 'error'
      default: return 'default'
    }
  }

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'system': return <Storage />
      case 'browser': return <History />
      case 'personal': return <ContentPaste />
      default: return <DataObject />
    }
  }

  const DatabaseCard = ({ database }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {getCategoryIcon(database.category)}
            <Typography variant="h6" component="div">
              {database.name}
            </Typography>
          </Box>
          <Chip 
            label={database.status} 
            color={getStatusColor(database.status)}
            size="small"
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary" paragraph>
          {database.description || 'No description provided'}
        </Typography>
        
        <Box display="flex" gap={1} mb={2}>
          <Chip label={database.category} size="small" variant="outlined" />
          {database.template && (
            <Chip label={`Template: ${database.template}`} size="small" variant="outlined" />
          )}
        </Box>
        
        <Typography variant="caption" color="text.secondary">
          Created: {new Date(database.created).toLocaleDateString()}
        </Typography>
        <br />
        <Typography variant="caption" color="text.secondary">
          Records: {database.recordCount || 0} | Size: {database.size || 0} bytes
        </Typography>
      </CardContent>
      
      <CardActions>
        {database.status === 'active' ? (
          <Button 
            size="small" 
            startIcon={<LinkOff />}
            onClick={() => handleDisconnectDatabase(database.id)}
          >
            Disconnect
          </Button>
        ) : (
          <Button 
            size="small" 
            startIcon={<Link />}
            onClick={() => handleConnectDatabase(database.id)}
          >
            Connect
          </Button>
        )}
        
        <Button 
          size="small" 
          startIcon={<Backup />}
          onClick={() => handleBackupDatabase(database.id)}
          disabled={database.status !== 'active'}
        >
          Backup
        </Button>
        
        <IconButton 
          size="small" 
          color="error"
          onClick={() => {
            setSelectedDatabase(database)
            setRemoveDialog(true)
          }}
        >
          <Delete />
        </IconButton>
      </CardActions>
    </Card>
  )

  const StatisticsOverview = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
          Database Statistics
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="primary">
                {statistics.total || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Databases
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="success.main">
                {statistics.active || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Connections
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="info.main">
                {statistics.totalRecords || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Records
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="warning.main">
                {Math.round((statistics.totalSize || 0) / 1024)} KB
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Size
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )

  const QuickActions = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Stack direction="row" spacing={2} flexWrap="wrap">
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddDialog(true)}
          >
            Add Database
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadDatabases}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<ContentPaste />}
            onClick={() => {
              setNewDatabase({
                ...newDatabase,
                id: 'clipboard_' + Date.now(),
                name: 'Clipboard Database',
                template: 'clipboard',
                category: 'system'
              })
              setAddDialog(true)
            }}
          >
            Add Clipboard DB
          </Button>
          <Button
            variant="outlined"
            startIcon={<History />}
            onClick={() => {
              setNewDatabase({
                ...newDatabase,
                id: 'history_' + Date.now(),
                name: 'Browser History',
                template: 'browser_history',
                category: 'browser'
              })
              setAddDialog(true)
            }}
          >
            Add History DB
          </Button>
        </Stack>
      </CardContent>
    </Card>
  )

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Typography variant="h4" gutterBottom>
        Database Management
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Add, remove, and manage multiple databases including clipboard, browser history, and custom databases.
      </Typography>

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

      {/* Statistics Overview */}
      <StatisticsOverview />

      {/* Quick Actions */}
      <QuickActions />

      {/* Database List */}
      <Typography variant="h5" gutterBottom>
        Registered Databases
      </Typography>
      
      {databases.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Storage sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No databases registered
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Add your first database to get started with data management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddDialog(true)}
          >
            Add Database
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {databases.map((database) => (
            <Grid item xs={12} md={6} lg={4} key={database.id}>
              <DatabaseCard database={database} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Add Database Dialog */}
      <Dialog open={addDialog} onClose={() => setAddDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Database</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Database ID"
              value={newDatabase.id}
              onChange={(e) => setNewDatabase({ ...newDatabase, id: e.target.value })}
              fullWidth
              required
              helperText="Unique identifier for the database"
            />
            
            <TextField
              label="Database Name"
              value={newDatabase.name}
              onChange={(e) => setNewDatabase({ ...newDatabase, name: e.target.value })}
              fullWidth
              required
            />
            
            <TextField
              label="Description"
              value={newDatabase.description}
              onChange={(e) => setNewDatabase({ ...newDatabase, description: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
            
            <FormControl fullWidth>
              <InputLabel>Template</InputLabel>
              <Select
                value={newDatabase.template}
                onChange={(e) => setNewDatabase({ ...newDatabase, template: e.target.value })}
                label="Template"
              >
                <MenuItem value="">Custom Database</MenuItem>
                <MenuItem value="clipboard">Clipboard Database</MenuItem>
                <MenuItem value="browser_history">Browser History</MenuItem>
                <MenuItem value="bookmarks">Bookmarks</MenuItem>
                <MenuItem value="notes">Notes Database</MenuItem>
                <MenuItem value="contacts">Contacts Database</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={newDatabase.category}
                onChange={(e) => setNewDatabase({ ...newDatabase, category: e.target.value })}
                label="Category"
              >
                <MenuItem value="system">System</MenuItem>
                <MenuItem value="browser">Browser</MenuItem>
                <MenuItem value="personal">Personal</MenuItem>
                <MenuItem value="custom">Custom</MenuItem>
              </Select>
            </FormControl>
            
            <FormControlLabel
              control={
                <Switch
                  checked={newDatabase.autoConnect}
                  onChange={(e) => setNewDatabase({ ...newDatabase, autoConnect: e.target.checked })}
                />
              }
              label="Auto-connect after creation"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialog(false)}>Cancel</Button>
          <Button onClick={handleAddDatabase} variant="contained">
            Add Database
          </Button>
        </DialogActions>
      </Dialog>

      {/* Remove Database Dialog */}
      <Dialog open={removeDialog} onClose={() => setRemoveDialog(false)}>
        <DialogTitle>Remove Database</DialogTitle>
        <DialogContent>
          {selectedDatabase && (
            <Box>
              <Typography variant="body1" paragraph>
                Are you sure you want to remove the database "{selectedDatabase.name}"?
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={removeOptions.backup}
                    onChange={(e) => setRemoveOptions({ ...removeOptions, backup: e.target.checked })}
                  />
                }
                label="Create backup before removal"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={removeOptions.deleteData}
                    onChange={(e) => setRemoveOptions({ ...removeOptions, deleteData: e.target.checked })}
                  />
                }
                label="Delete all data (cannot be undone)"
              />
              
              {removeOptions.deleteData && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  This will permanently delete all data in the database. This action cannot be undone.
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemoveDialog(false)}>Cancel</Button>
          <Button onClick={handleRemoveDatabase} color="error" variant="contained">
            Remove Database
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default DatabaseManagementPanel
