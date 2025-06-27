import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Switch,
  FormControlLabel,
  Alert,
  Avatar,
  Stack,
  Tooltip,
  IconButton,
  Badge,
  Skeleton,
  ToggleButton,
  ToggleButtonGroup,
  Button,
  ButtonGroup,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { 
  green, red, orange, blue, grey 
} from '@mui/material/colors';
import {
  Memory,
  Security,
  Speed,
  Warning,
  CheckCircle,
  Error,
  Info,
  Refresh,
  TrendingUp,
  Remove,
  PlayArrow,
  Stop,
  Pause,
  Settings,
  ExpandMore,
  SignalWifiStatusbar4Bar,
  SignalWifiOff,
  Timeline,
  ShowChart
} from '@mui/icons-material';
import * as d3 from 'd3';
import io from 'socket.io-client';

const ImprovedMemoryDashboard = () => {
  const [memoryData, setMemoryData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timelineData, setTimelineData] = useState([]);
  const [timeRange, setTimeRange] = useState('5m'); // 5m, 15m, 1h, 6h
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(2000); // 2 seconds
  const socketRef = useRef(null);
  const chartRef = useRef(null);
  const timelineRef = useRef(null);

  // Initialize WebSocket connection with robust error handling
  useEffect(() => {
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 2000;

    const connectSocket = () => {
      const socket = io('http://localhost:3002', {
        transports: ['websocket', 'polling'],
        timeout: 5000,
        reconnection: true,
        reconnectionAttempts: maxReconnectAttempts,
        reconnectionDelay: reconnectDelay
      });

      socketRef.current = socket;

      socket.on('connect', () => {
        console.log('Memory monitoring connected');
        setIsConnected(true);
        setError(null);
        setLoading(false);
        reconnectAttempts = 0;

        // Start monitoring immediately on connection
        socket.emit('start_monitoring');
        setIsMonitoring(true);
      });

      socket.on('disconnect', (reason) => {
        console.log('Memory monitoring disconnected:', reason);
        setIsConnected(false);
        setIsMonitoring(false);

        if (reason === 'io server disconnect') {
          // Server initiated disconnect, try to reconnect
          setTimeout(() => {
            if (reconnectAttempts < maxReconnectAttempts) {
              reconnectAttempts++;
              connectSocket();
            }
          }, reconnectDelay);
        }
      });

      socket.on('memory_update', (data) => {
        if (data && data.memory) {
          setMemoryData(data);
          updateChart(data);
          updateTimelineData(data);
          setError(null); // Clear any previous errors
        }
      });

      socket.on('connect_error', (err) => {
        console.error('Memory monitoring connection error:', err);
        setError(`Connection failed: ${err.message || 'Unable to connect to memory monitoring service'}`);
        setLoading(false);
        setIsConnected(false);
      });

      socket.on('reconnect_failed', () => {
        setError('Failed to reconnect to memory monitoring service after multiple attempts');
        setLoading(false);
      });
    };

    connectSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  // Update timeline chart when data changes with debouncing
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      updateTimelineChart();
    }, 100); // Debounce updates to prevent excessive re-renders

    return () => clearTimeout(timeoutId);
  }, [timelineData, timeRange]);

  // Auto-refresh mechanism for fallback when WebSocket fails
  useEffect(() => {
    let intervalId;

    if (autoRefresh && !isConnected) {
      intervalId = setInterval(async () => {
        try {
          const response = await fetch('http://localhost:3002/api/memory');
          if (response.ok) {
            const data = await response.json();
            setMemoryData(data);
            updateChart(data);
            updateTimelineData(data);
            setError(null);
          }
        } catch (err) {
          console.warn('Fallback fetch failed:', err);
        }
      }, refreshInterval);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [autoRefresh, isConnected, refreshInterval]);

  // Toggle monitoring
  const toggleMonitoring = () => {
    if (socketRef.current) {
      if (isMonitoring) {
        socketRef.current.emit('stop_monitoring');
        setIsMonitoring(false);
      } else {
        socketRef.current.emit('start_monitoring');
        setIsMonitoring(true);
      }
    }
  };

  // Update timeline data with new memory readings
  const updateTimelineData = (data) => {
    if (!data?.memory) return;

    const now = new Date();
    const newDataPoint = {
      timestamp: now,
      memory: data.memory.memory.percent,
      swap: data.memory.swap.percent,
      memoryUsed: data.memory.memory.used,
      swapUsed: data.memory.swap.used
    };

    setTimelineData(prevData => {
      const maxPoints = getMaxDataPoints();
      const updatedData = [...prevData, newDataPoint];

      // Keep only the data points within the selected time range
      const cutoffTime = new Date(now.getTime() - getTimeRangeMs());
      const filteredData = updatedData.filter(point => point.timestamp >= cutoffTime);

      // Limit to max points to prevent memory issues
      const finalData = filteredData.slice(-maxPoints);

      // Ensure we have at least a few data points for meaningful visualization
      if (finalData.length < 2) {
        // Add some initial dummy data points to show the timeline properly
        const dummyPoint = {
          timestamp: new Date(now.getTime() - 30000), // 30 seconds ago
          memory: newDataPoint.memory,
          swap: newDataPoint.swap,
          memoryUsed: newDataPoint.memoryUsed,
          swapUsed: newDataPoint.swapUsed,
          available: data.memory.memory.available,
          cached: data.memory.memory.cached || 0,
          buffers: data.memory.memory.buffers || 0
        };
        return [dummyPoint, newDataPoint];
      }

      return finalData;
    });
  };

  // Get maximum data points based on time range
  const getMaxDataPoints = () => {
    switch (timeRange) {
      case '5m': return 300;   // 5 minutes * 60 seconds
      case '15m': return 900;  // 15 minutes * 60 seconds
      case '1h': return 1800;  // 1 hour * 30 (every 2 seconds)
      case '6h': return 2160;  // 6 hours * 6 (every 10 seconds)
      default: return 300;
    }
  };

  // Get time range in milliseconds
  const getTimeRangeMs = () => {
    switch (timeRange) {
      case '5m': return 5 * 60 * 1000;
      case '15m': return 15 * 60 * 1000;
      case '1h': return 60 * 60 * 1000;
      case '6h': return 6 * 60 * 60 * 1000;
      default: return 5 * 60 * 1000;
    }
  };

  // Enhanced D3.js Chart
  const updateChart = (data) => {
    if (!data?.memory || !chartRef.current) return;

    const svg = d3.select(chartRef.current);
    svg.selectAll("*").remove();

    const width = 500;
    const height = 180;
    const margin = { top: 20, right: 20, bottom: 40, left: 60 };

    const memoryPercent = data.memory.memory.percent;
    const swapPercent = data.memory.swap.percent;

    const chartData = [
      { 
        name: 'Memory', 
        value: memoryPercent, 
        color: memoryPercent > 80 ? red[500] : memoryPercent > 60 ? orange[500] : green[500],
        icon: '🧠'
      },
      { 
        name: 'Swap', 
        value: swapPercent, 
        color: swapPercent > 50 ? red[500] : swapPercent > 25 ? orange[500] : blue[500],
        icon: '💾'
      }
    ];

    const xScale = d3.scaleBand()
      .domain(chartData.map(d => d.name))
      .range([margin.left, width - margin.right])
      .padding(0.3);

    const yScale = d3.scaleLinear()
      .domain([0, 100])
      .range([height - margin.bottom, margin.top]);

    svg.attr('width', width).attr('height', height);

    // Add gradient definitions
    const defs = svg.append('defs');
    chartData.forEach((d, i) => {
      const gradient = defs.append('linearGradient')
        .attr('id', `gradient-${i}`)
        .attr('gradientUnits', 'userSpaceOnUse')
        .attr('x1', 0).attr('y1', height)
        .attr('x2', 0).attr('y2', 0);
      
      gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', d.color)
        .attr('stop-opacity', 0.8);
      
      gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', d.color)
        .attr('stop-opacity', 0.4);
    });

    // Add bars with animation
    svg.selectAll('.bar')
      .data(chartData)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', d => xScale(d.name))
      .attr('y', height - margin.bottom)
      .attr('width', xScale.bandwidth())
      .attr('height', 0)
      .attr('fill', (d, i) => `url(#gradient-${i})`)
      .attr('rx', 8)
      .transition()
      .duration(800)
      .attr('y', d => yScale(d.value))
      .attr('height', d => height - margin.bottom - yScale(d.value));

    // Add value labels with icons
    svg.selectAll('.label')
      .data(chartData)
      .enter()
      .append('text')
      .attr('class', 'label')
      .attr('x', d => xScale(d.name) + xScale.bandwidth() / 2)
      .attr('y', d => yScale(d.value) - 10)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', 'bold')
      .style('fill', '#333')
      .text(d => `${d.value.toFixed(1)}%`);

    // Add x-axis with icons
    const xAxis = svg.append('g')
      .attr('transform', `translate(0,${height - margin.bottom})`);
    
    chartData.forEach(d => {
      xAxis.append('text')
        .attr('x', xScale(d.name) + xScale.bandwidth() / 2)
        .attr('y', 20)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .text(d.icon);
      
      xAxis.append('text')
        .attr('x', xScale(d.name) + xScale.bandwidth() / 2)
        .attr('y', 35)
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .style('fill', '#666')
        .text(d.name);
    });

    // Add y-axis
    svg.append('g')
      .attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(yScale).tickFormat(d => `${d}%`));
  };

  // Enhanced Timeline Chart with real-time updates
  const updateTimelineChart = () => {
    if (!timelineData.length || !timelineRef.current) return;

    const svg = d3.select(timelineRef.current);
    svg.selectAll("*").remove();

    const width = 800;
    const height = 300;
    const margin = { top: 20, right: 80, bottom: 40, left: 60 };

    // Set up scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(timelineData, d => d.timestamp))
      .range([margin.left, width - margin.right]);

    const yScale = d3.scaleLinear()
      .domain([0, 100])
      .range([height - margin.bottom, margin.top]);

    svg.attr('width', width).attr('height', height);

    // Add gradient definitions for area charts
    const defs = svg.append('defs');

    // Memory gradient
    const memoryGradient = defs.append('linearGradient')
      .attr('id', 'memoryGradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', height)
      .attr('x2', 0).attr('y2', 0);

    memoryGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', blue[500])
      .attr('stop-opacity', 0.1);

    memoryGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', blue[500])
      .attr('stop-opacity', 0.6);

    // Swap gradient
    const swapGradient = defs.append('linearGradient')
      .attr('id', 'swapGradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', height)
      .attr('x2', 0).attr('y2', 0);

    swapGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', orange[500])
      .attr('stop-opacity', 0.1);

    swapGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', orange[500])
      .attr('stop-opacity', 0.6);

    // Create line generators
    const memoryLine = d3.line()
      .x(d => xScale(d.timestamp))
      .y(d => yScale(d.memory))
      .curve(d3.curveMonotoneX);

    const swapLine = d3.line()
      .x(d => xScale(d.timestamp))
      .y(d => yScale(d.swap))
      .curve(d3.curveMonotoneX);

    // Create area generators
    const memoryArea = d3.area()
      .x(d => xScale(d.timestamp))
      .y0(height - margin.bottom)
      .y1(d => yScale(d.memory))
      .curve(d3.curveMonotoneX);

    const swapArea = d3.area()
      .x(d => xScale(d.timestamp))
      .y0(height - margin.bottom)
      .y1(d => yScale(d.swap))
      .curve(d3.curveMonotoneX);

    // Add grid lines
    svg.append('g')
      .attr('class', 'grid')
      .attr('transform', `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(xScale)
        .tickSize(-height + margin.top + margin.bottom)
        .tickFormat('')
      )
      .style('stroke-dasharray', '3,3')
      .style('opacity', 0.3);

    svg.append('g')
      .attr('class', 'grid')
      .attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(yScale)
        .tickSize(-width + margin.left + margin.right)
        .tickFormat('')
      )
      .style('stroke-dasharray', '3,3')
      .style('opacity', 0.3);

    // Add area charts
    svg.append('path')
      .datum(timelineData)
      .attr('fill', 'url(#memoryGradient)')
      .attr('d', memoryArea);

    svg.append('path')
      .datum(timelineData)
      .attr('fill', 'url(#swapGradient)')
      .attr('d', swapArea);

    // Add line charts
    svg.append('path')
      .datum(timelineData)
      .attr('fill', 'none')
      .attr('stroke', blue[600])
      .attr('stroke-width', 2)
      .attr('d', memoryLine);

    svg.append('path')
      .datum(timelineData)
      .attr('fill', 'none')
      .attr('stroke', orange[600])
      .attr('stroke-width', 2)
      .attr('d', swapLine);

    // Add axes
    svg.append('g')
      .attr('transform', `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat('%H:%M:%S')));

    svg.append('g')
      .attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(yScale).tickFormat(d => `${d}%`));

    // Add legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - margin.right + 10}, ${margin.top})`);

    legend.append('circle')
      .attr('cx', 0)
      .attr('cy', 0)
      .attr('r', 6)
      .style('fill', blue[600]);

    legend.append('text')
      .attr('x', 15)
      .attr('y', 0)
      .attr('dy', '0.35em')
      .style('font-size', '12px')
      .text('Memory');

    legend.append('circle')
      .attr('cx', 0)
      .attr('cy', 20)
      .attr('r', 6)
      .style('fill', orange[600]);

    legend.append('text')
      .attr('x', 15)
      .attr('y', 20)
      .attr('dy', '0.35em')
      .style('font-size', '12px')
      .text('Swap');

    // Add current values as dots
    if (timelineData.length > 0) {
      const lastPoint = timelineData[timelineData.length - 1];

      svg.append('circle')
        .attr('cx', xScale(lastPoint.timestamp))
        .attr('cy', yScale(lastPoint.memory))
        .attr('r', 4)
        .attr('fill', blue[600])
        .attr('stroke', 'white')
        .attr('stroke-width', 2);

      svg.append('circle')
        .attr('cx', xScale(lastPoint.timestamp))
        .attr('cy', yScale(lastPoint.swap))
        .attr('r', 4)
        .attr('fill', orange[600])
        .attr('stroke', 'white')
        .attr('stroke-width', 2);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getProtectionStatus = () => {
    if (!memoryData?.protection) return { 
      color: 'default', 
      text: 'Unknown', 
      icon: <Info />,
      severity: 'info'
    };
    
    const activeTiers = memoryData.protection.total_active_tiers || 0;
    if (activeTiers >= 2) return { 
      color: 'success', 
      text: `${activeTiers} Tiers Active`, 
      icon: <Security />,
      severity: 'success'
    };
    if (activeTiers === 1) return { 
      color: 'warning', 
      text: '1 Tier Active', 
      icon: <Warning />,
      severity: 'warning'
    };
    return { 
      color: 'error', 
      text: 'No Protection', 
      icon: <Error />,
      severity: 'error'
    };
  };

  const getMemoryStatus = () => {
    if (!memoryData?.memory) return { severity: 'info', message: 'Loading...' };
    
    const percent = memoryData.memory.memory.percent;
    if (percent > 85) return { severity: 'error', message: 'Critical memory usage' };
    if (percent > 70) return { severity: 'warning', message: 'High memory usage' };
    return { severity: 'success', message: 'Memory usage normal' };
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          🛡️ Memory Protection Dashboard
        </Typography>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((item) => (
            <Grid item xs={12} md={6} key={item}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="60%" height={32} />
                  <Skeleton variant="rectangular" width="100%" height={100} sx={{ mt: 2 }} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert 
        severity="error" 
        sx={{ m: 2 }}
        action={
          <IconButton color="inherit" size="small" onClick={() => window.location.reload()}>
            <Refresh />
          </IconButton>
        }
      >
        {error}
      </Alert>
    );
  }

  const protectionStatus = getProtectionStatus();
  const memoryStatus = getMemoryStatus();

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          🛡️ Memory Protection Dashboard
          <Badge 
            color={isConnected ? 'success' : 'error'} 
            variant="dot"
            sx={{ ml: 1 }}
          >
            {isConnected ? <SignalWifiStatusbar4Bar /> : <SignalWifiOff />}
          </Badge>
        </Typography>
        
        <Stack direction="row" spacing={2} alignItems="center">
          <Chip 
            icon={protectionStatus.icon}
            label={protectionStatus.text} 
            color={protectionStatus.color}
            variant="outlined"
          />
          <FormControlLabel
            control={
              <Switch
                checked={isMonitoring}
                onChange={toggleMonitoring}
                disabled={!isConnected}
                icon={<Stop />}
                checkedIcon={<PlayArrow />}
              />
            }
            label={isMonitoring ? "Live Monitoring" : "Start Monitoring"}
          />
        </Stack>
      </Box>

      {/* Enhanced Control Panel */}
      <Accordion sx={{ mb: 3 }}>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Settings /> Advanced Controls
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3} alignItems="center">
            {/* Monitoring Controls */}
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Monitoring Controls
              </Typography>
              <ButtonGroup variant="outlined" size="small" fullWidth>
                <Button
                  startIcon={isMonitoring ? <Pause /> : <PlayArrow />}
                  onClick={toggleMonitoring}
                  color={isMonitoring ? "warning" : "success"}
                  disabled={!isConnected}
                >
                  {isMonitoring ? 'Pause' : 'Start'}
                </Button>
                <Button
                  startIcon={<Stop />}
                  onClick={() => {
                    if (socketRef.current) {
                      socketRef.current.emit('stop_monitoring');
                      setIsMonitoring(false);
                    }
                  }}
                  color="error"
                  disabled={!isConnected}
                >
                  Stop
                </Button>
                <Button
                  startIcon={<Refresh />}
                  onClick={() => window.location.reload()}
                >
                  Reset
                </Button>
              </ButtonGroup>
            </Grid>

            {/* Refresh Interval */}
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Refresh Interval: {refreshInterval / 1000}s
              </Typography>
              <Slider
                value={refreshInterval}
                onChange={(e, newValue) => setRefreshInterval(newValue)}
                min={1000}
                max={10000}
                step={1000}
                marks={[
                  { value: 1000, label: '1s' },
                  { value: 5000, label: '5s' },
                  { value: 10000, label: '10s' }
                ]}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${value / 1000}s`}
                size="small"
              />
            </Grid>

            {/* Connection Status */}
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Connection Status
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {isConnected ? (
                  <>
                    <SignalWifiStatusbar4Bar color="success" />
                    <Typography variant="body2" color="success.main">
                      Connected (WebSocket)
                    </Typography>
                  </>
                ) : (
                  <>
                    <SignalWifiOff color="error" />
                    <Typography variant="body2" color="error.main">
                      Disconnected
                    </Typography>
                  </>
                )}
              </Box>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Status Alert */}
      {memoryData && (
        <Alert 
          severity={memoryStatus.severity} 
          sx={{ mb: 3 }}
          icon={protectionStatus.icon}
        >
          {memoryStatus.message} • {protectionStatus.text}
        </Alert>
      )}

      {memoryData && (
        <Grid container spacing={3}>
          {/* Timeline Chart - Full Width */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Timeline /> Memory & Swap Usage Timeline
                    {isMonitoring && (
                      <Chip size="small" label="Live" color="success" variant="outlined" />
                    )}
                  </Typography>
                  <ToggleButtonGroup
                    value={timeRange}
                    exclusive
                    onChange={(event, newTimeRange) => {
                      if (newTimeRange !== null) {
                        setTimeRange(newTimeRange);
                      }
                    }}
                    size="small"
                  >
                    <ToggleButton value="5m">5m</ToggleButton>
                    <ToggleButton value="15m">15m</ToggleButton>
                    <ToggleButton value="1h">1h</ToggleButton>
                    <ToggleButton value="6h">6h</ToggleButton>
                  </ToggleButtonGroup>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <svg ref={timelineRef}></svg>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Memory Usage Overview */}
          <Grid item xs={12} md={8}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ShowChart /> Current Usage
                  {isMonitoring && (
                    <Chip size="small" label="Live" color="success" variant="outlined" />
                  )}
                </Typography>
                <svg ref={chartRef}></svg>
              </CardContent>
            </Card>
          </Grid>

          {/* Protection Status Details */}
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Security /> Protection Layers
                </Typography>
                <Stack spacing={2}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar sx={{ bgcolor: memoryData.protection.tier1_earlyoom ? green[500] : grey[300], width: 32, height: 32 }}>
                      {memoryData.protection.tier1_earlyoom ? <CheckCircle /> : <Remove />}
                    </Avatar>
                    <Box>
                      <Typography variant="body2" fontWeight="bold">Tier 1 (earlyoom)</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Proactive OOM prevention
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar sx={{ bgcolor: memoryData.protection.tier2_nohang ? green[500] : grey[300], width: 32, height: 32 }}>
                      {memoryData.protection.tier2_nohang ? <CheckCircle /> : <Remove />}
                    </Avatar>
                    <Box>
                      <Typography variant="body2" fontWeight="bold">Tier 2 (nohang)</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Advanced memory management
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar sx={{ bgcolor: memoryData.protection.tier3_systemd_oomd ? green[500] : grey[300], width: 32, height: 32 }}>
                      {memoryData.protection.tier3_systemd_oomd ? <CheckCircle /> : <Remove />}
                    </Avatar>
                    <Box>
                      <Typography variant="body2" fontWeight="bold">Tier 3 (systemd-oomd)</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Emergency fallback
                      </Typography>
                    </Box>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          {/* Memory Statistics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Speed /> Memory Statistics
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color={memoryData.memory.memory.percent > 80 ? 'error' : 'primary'}>
                        {memoryData.memory.memory.percent.toFixed(1)}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">Memory Used</Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={memoryData.memory.memory.percent} 
                        sx={{ mt: 1 }}
                        color={memoryData.memory.memory.percent > 80 ? 'error' : memoryData.memory.memory.percent > 60 ? 'warning' : 'success'}
                      />
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {formatBytes(memoryData.memory.memory.used)} / {formatBytes(memoryData.memory.memory.total)}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color={memoryData.memory.swap.percent > 50 ? 'error' : 'primary'}>
                        {memoryData.memory.swap.percent.toFixed(1)}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">Swap Used</Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={memoryData.memory.swap.percent} 
                        sx={{ mt: 1 }}
                        color={memoryData.memory.swap.percent > 50 ? 'error' : memoryData.memory.swap.percent > 25 ? 'warning' : 'primary'}
                      />
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {formatBytes(memoryData.memory.swap.used)} / {formatBytes(memoryData.memory.swap.total)}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* High-Risk Processes */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Warning /> High-Risk Processes
                  <Tooltip title="Processes with highest OOM (Out of Memory) scores">
                    <IconButton size="small">
                      <Info fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Process</TableCell>
                        <TableCell align="center">Risk</TableCell>
                        <TableCell align="right">Memory</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {memoryData.top_processes?.slice(0, 5).map((proc, index) => (
                        <TableRow key={index} hover>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {proc.name}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Chip 
                              label={proc.oom_score} 
                              size="small"
                              color={proc.oom_score > 800 ? 'error' : proc.oom_score > 500 ? 'warning' : 'default'}
                              icon={proc.oom_score > 800 ? <TrendingUp /> : <Remove />}
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2">
                              {proc.vmrss}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default ImprovedMemoryDashboard;
