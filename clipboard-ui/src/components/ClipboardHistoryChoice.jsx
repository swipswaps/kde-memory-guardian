import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  Chip,
  Stack,
  Grid
} from '@mui/material'
import {
  ContentPaste,
  History,
  Storage,
  CheckCircle,
  Settings,
  PlayArrow,
  Info
} from '@mui/icons-material'
import DatabaseManager from '../services/DatabaseManager'

function ClipboardHistoryChoice({ onSetupComplete }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [setupDialog, setSetupDialog] = useState(false)
  const [clipboardEnabled, setClipboardEnabled] = useState(true)
  const [autoCapture, setAutoCapture] = useState(true)
  const [setupProgress, setSetupProgress] = useState(0)

  const handleQuickSetup = async () => {
    setLoading(true)
    setSetupProgress(0)
    
    try {
      // Step 1: Initialize database
      setSetupProgress(25)
      await DatabaseManager.initializeDatabase()
      
      // Step 2: Create sample clipboard entries
      setSetupProgress(50)
      const sampleEntries = [
        {
          content: 'Welcome to Clipboard Intelligence!',
          content_type: 'Text',
          timestamp: new Date().toISOString(),
          source: 'setup'
        },
        {
          content: 'https://github.com/user/clipboard-intelligence',
          content_type: 'URL',
          timestamp: new Date(Date.now() - 60000).toISOString(),
          source: 'setup'
        },
        {
          content: '{"message": "Clipboard data can be JSON too!"}',
          content_type: 'JSON',
          timestamp: new Date(Date.now() - 120000).toISOString(),
          source: 'setup'
        }
      ]
      
      // Step 3: Add sample data
      setSetupProgress(75)
      for (const entry of sampleEntries) {
        await DatabaseManager.createClipboardEntry(entry)
      }
      
      // Step 4: Complete setup
      setSetupProgress(100)
      setSuccess('Clipboard history database set up successfully with sample data!')
      
      if (onSetupComplete) {
        onSetupComplete()
      }
      
      setSetupDialog(false)
    } catch (err) {
      setError('Setup failed: ' + err.message)
    } finally {
      setLoading(false)
      setSetupProgress(0)
    }
  }

  const handleCustomSetup = () => {
    setSetupDialog(true)
  }

  const executeCustomSetup = async () => {
    setLoading(true)
    try {
      await DatabaseManager.initializeDatabase()
      
      if (clipboardEnabled) {
        // Create initial entry
        await DatabaseManager.createClipboardEntry({
          content: 'Clipboard history tracking enabled',
          content_type: 'Text',
          timestamp: new Date().toISOString(),
          source: 'user_setup'
        })
      }
      
      setSuccess(`Clipboard history ${clipboardEnabled ? 'enabled' : 'disabled'} successfully!`)
      setSetupDialog(false)
      
      if (onSetupComplete) {
        onSetupComplete()
      }
    } catch (err) {
      setError('Custom setup failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Typography variant="h4" gutterBottom>
        <ContentPaste sx={{ mr: 1, verticalAlign: 'middle' }} />
        Clipboard History Setup
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Choose how you want to set up clipboard history tracking and data management.
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
      {loading && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress variant="determinate" value={setupProgress} />
          <Typography variant="body2" sx={{ mt: 1 }}>
            Setup progress: {setupProgress}%
          </Typography>
        </Box>
      )}

      {/* Setup Options */}
      <Grid container spacing={3}>
        {/* Quick Setup */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <PlayArrow color="primary" />
                <Typography variant="h6">
                  Quick Setup
                </Typography>
                <Chip label="Recommended" size="small" color="primary" />
              </Box>
              
              <Typography variant="body2" color="text.secondary" paragraph>
                Automatically sets up clipboard history tracking with sample data and optimal settings.
              </Typography>
              
              <Stack spacing={1}>
                <Box display="flex" alignItems="center" gap={1}>
                  <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                  <Typography variant="body2">
                    Clipboard history database
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center" gap={1}>
                  <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                  <Typography variant="body2">
                    Sample data for testing
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center" gap={1}>
                  <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                  <Typography variant="body2">
                    Automatic content type detection
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center" gap={1}>
                  <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                  <Typography variant="body2">
                    Search and analytics ready
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
            <CardActions>
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={handleQuickSetup}
                disabled={loading}
                fullWidth
              >
                Quick Setup
              </Button>
            </CardActions>
          </Card>
        </Grid>

        {/* Custom Setup */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Settings color="secondary" />
                <Typography variant="h6">
                  Custom Setup
                </Typography>
              </Box>
              
              <Typography variant="body2" color="text.secondary" paragraph>
                Configure clipboard history tracking with your preferred settings and options.
              </Typography>
              
              <Stack spacing={2}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={clipboardEnabled}
                      onChange={(e) => setClipboardEnabled(e.target.checked)}
                    />
                  }
                  label="Enable clipboard history tracking"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={autoCapture}
                      onChange={(e) => setAutoCapture(e.target.checked)}
                      disabled={!clipboardEnabled}
                    />
                  }
                  label="Automatic content capture"
                />
                
                <Alert severity="info" icon={<Info />}>
                  Custom setup allows you to configure specific options for your workflow.
                </Alert>
              </Stack>
            </CardContent>
            <CardActions>
              <Button
                variant="outlined"
                startIcon={<Settings />}
                onClick={handleCustomSetup}
                disabled={loading}
                fullWidth
              >
                Custom Setup
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>

      {/* Features Overview */}
      <Paper sx={{ p: 3, mt: 3, bgcolor: 'grey.50' }}>
        <Typography variant="h6" gutterBottom>
          <History sx={{ mr: 1, verticalAlign: 'middle' }} />
          Clipboard History Features
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <Typography variant="subtitle2" gutterBottom>
              Content Types
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Text, URLs, JSON, CSV, Email addresses, and more
            </Typography>
          </Grid>
          <Grid item xs={12} md={3}>
            <Typography variant="subtitle2" gutterBottom>
              Search & Filter
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Full-text search, content type filtering, date ranges
            </Typography>
          </Grid>
          <Grid item xs={12} md={3}>
            <Typography variant="subtitle2" gutterBottom>
              Analytics
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Usage patterns, content analysis, Neo4j visualizations
            </Typography>
          </Grid>
          <Grid item xs={12} md={3}>
            <Typography variant="subtitle2" gutterBottom>
              Export & Backup
            </Typography>
            <Typography variant="body2" color="text.secondary">
              JSON/CSV export, database backup, data portability
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Custom Setup Dialog */}
      <Dialog open={setupDialog} onClose={() => setSetupDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Custom Clipboard Setup</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={clipboardEnabled}
                  onChange={(e) => setClipboardEnabled(e.target.checked)}
                />
              }
              label="Enable clipboard history tracking"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={autoCapture}
                  onChange={(e) => setAutoCapture(e.target.checked)}
                  disabled={!clipboardEnabled}
                />
              }
              label="Automatic content capture"
            />
            
            <Alert severity="info">
              {clipboardEnabled 
                ? "Clipboard history will be tracked and stored locally in your browser."
                : "Clipboard history tracking will be disabled. You can enable it later."
              }
            </Alert>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSetupDialog(false)}>Cancel</Button>
          <Button 
            onClick={executeCustomSetup} 
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Setting up...' : 'Apply Settings'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ClipboardHistoryChoice
