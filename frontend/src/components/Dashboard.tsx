import React, { useState } from 'react';
import { useUser, UserButton } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  AppBar,
  Toolbar,
  Grid,
  Card,
  CardContent,
  Button,
  Stack,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Chat,
  AdminPanelSettings,
  Analytics,
  Settings,
  TrendingUp,
  People,
  Support,
  Speed,
} from '@mui/icons-material';

const Dashboard: React.FC = () => {
  const { user } = useUser();
  const navigate = useNavigate();

  const stats = [
    {
      title: 'Total Conversations',
      value: '1,234',
      change: '+12%',
      icon: <Chat />,
      color: '#3b82f6',
    },
    {
      title: 'Active Users',
      value: '89',
      change: '+5%',
      icon: <People />,
      color: '#10b981',
    },
    {
      title: 'Resolution Rate',
      value: '94%',
      change: '+2%',
      icon: <TrendingUp />,
      color: '#8b5cf6',
    },
    {
      title: 'Avg Response Time',
      value: '1.2s',
      change: '-15%',
      icon: <Speed />,
      color: '#f59e0b',
    },
  ];

  const quickActions = [
    {
      title: 'Start Chat Session',
      description: 'Begin a new customer support conversation',
      icon: <Chat />,
      action: () => navigate('/chat'),
      color: '#3b82f6',
    },
    {
      title: 'Admin Panel',
      description: 'Manage system settings and configurations',
      icon: <AdminPanelSettings />,
      action: () => navigate('/admin'),
      color: '#8b5cf6',
    },
    {
      title: 'Analytics',
      description: 'View detailed performance metrics',
      icon: <Analytics />,
      action: () => console.log('Analytics clicked'),
      color: '#10b981',
    },
    {
      title: 'Settings',
      description: 'Configure your account preferences',
      icon: <Settings />,
      action: () => console.log('Settings clicked'),
      color: '#f59e0b',
    },
  ];

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Navigation */}
      <AppBar position="static" sx={{ bgcolor: 'background.paper' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            SupportAI Dashboard
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="body2" color="text.secondary">
              Welcome, {user?.firstName}
            </Typography>
            <UserButton />
          </Stack>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Welcome Section */}
        <Box mb={4}>
          <Typography variant="h4" component="h1" sx={{ mb: 1, fontWeight: 'bold' }}>
            Welcome back, {user?.firstName}! 👋
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's what's happening with your customer support today.
          </Typography>
        </Box>

        {/* Stats Grid */}
        <Grid container spacing={3} mb={4}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 2,
                        bgcolor: `${stat.color}20`,
                        color: stat.color,
                      }}
                    >
                      {stat.icon}
                    </Box>
                    <Chip
                      label={stat.change}
                      size="small"
                      color={stat.change.startsWith('+') ? 'success' : 'error'}
                      variant="outlined"
                    />
                  </Stack>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.title}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Quick Actions */}
        <Typography variant="h5" component="h2" sx={{ mb: 3, fontWeight: 'bold' }}>
          Quick Actions
        </Typography>
        <Grid container spacing={3} mb={4}>
          {quickActions.map((action, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  },
                }}
                onClick={action.action}
              >
                <CardContent sx={{ textAlign: 'center', p: 3 }}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 3,
                      bgcolor: `${action.color}20`,
                      color: action.color,
                      display: 'inline-flex',
                      mb: 2,
                    }}
                  >
                    {action.icon}
                  </Box>
                  <Typography variant="h6" component="h3" sx={{ mb: 1, fontWeight: 'bold' }}>
                    {action.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {action.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Recent Activity */}
        <Card>
          <CardContent>
            <Typography variant="h6" component="h3" sx={{ mb: 3, fontWeight: 'bold' }}>
              Recent Activity
            </Typography>
            <Stack spacing={2}>
              {[
                { time: '2 minutes ago', action: 'New conversation started with customer #1234' },
                { time: '15 minutes ago', action: 'Support ticket resolved for customer #1233' },
                { time: '1 hour ago', action: 'System configuration updated' },
                { time: '2 hours ago', action: 'New user registered: john.doe@example.com' },
              ].map((activity, index) => (
                <Box key={index} sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    {activity.time}
                  </Typography>
                  <Typography variant="body1">{activity.action}</Typography>
                </Box>
              ))}
            </Stack>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Dashboard;