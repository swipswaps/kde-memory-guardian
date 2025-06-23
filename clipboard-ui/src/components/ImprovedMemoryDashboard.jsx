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
  Skeleton
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
  SignalWifiStatusbar4Bar,
  SignalWifiOff
} from '@mui/icons-material';
import * as d3 from 'd3';
import io from 'socket.io-client';

const ImprovedMemoryDashboard = () => {
  const [memoryData, setMemoryData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const socketRef = useRef(null);
  const chartRef = useRef(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const socket = io('http://localhost:3002');
    socketRef.current = socket;

    socket.on('connect', () => {
      setIsConnected(true);
      setError(null);
      setLoading(false);
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      setLoading(false);
    });

    socket.on('memory_update', (data) => {
      setMemoryData(data);
      updateChart(data);
    });

    socket.on('connect_error', (err) => {
      setError('Unable to connect to memory monitoring service');
      setLoading(false);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

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
          {/* Memory Usage Overview */}
          <Grid item xs={12} md={8}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Memory /> Memory & Swap Usage
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
