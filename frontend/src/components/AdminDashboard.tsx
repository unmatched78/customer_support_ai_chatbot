import React, { useState, useEffect } from 'react';
import { useUser, UserButton } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  AppBar,
  Toolbar,
  IconButton,
  Stack
} from '@mui/material';
import { Refresh, Edit, Add, ArrowBack } from '@mui/icons-material';
import axios from 'axios';
// Configure axios defaults
axios.defaults.baseURL = 'https://work-1-hsspmvshfbjjmzql.prod-runtime.all-hands.dev:12002';
interface Analytics {
  conversations: {
    total: number;
    active: number;
    escalated: number;
    resolved: number;
  };
  messages: {
    total: number;
    ai_messages: number;
    customer_messages: number;
  };
  actions: {
    total: number;
    refunds: number;
    subscription_changes: number;
  };
  recent_conversations: Array<{
    id: number;
    session_id: string;
    customer_email: string;
    status: string;
    message_count: number;
    created_at: string;
  }>;
}

interface SystemPrompt {
  id: number;
  name: string;
  content: string;
  description: string;
  is_active: boolean;
  department: string;
  created_at: string;
  updated_at: string | null;
}

const AdminDashboard: React.FC = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [prompts, setPrompts] = useState<SystemPrompt[]>([]);
  const [loading, setLoading] = useState(false);
  const [editPromptDialog, setEditPromptDialog] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState<SystemPrompt | null>(null);
  const [promptForm, setPromptForm] = useState({
    name: '',
    content: '',
    description: '',
    department: 'general'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [analyticsRes, promptsRes] = await Promise.all([
        axios.get('/api/v1/admin/analytics'),
        axios.get('/api/v1/admin/prompts')
      ]);
      
      setAnalytics(analyticsRes.data);
      setPrompts(promptsRes.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditPrompt = (prompt: SystemPrompt) => {
    setSelectedPrompt(prompt);
    setPromptForm({
      name: prompt.name,
      content: prompt.content,
      description: prompt.description,
      department: prompt.department
    });
    setEditPromptDialog(true);
  };

  const handleSavePrompt = async () => {
    try {
      if (selectedPrompt) {
        await axios.put(`/api/v1/admin/prompts/${selectedPrompt.id}`, promptForm);
      } else {
        await axios.post('/api/v1/admin/prompts', promptForm);
      }
      
      setEditPromptDialog(false);
      setSelectedPrompt(null);
      setPromptForm({ name: '', content: '', description: '', department: 'general' });
      await loadData();
    } catch (error) {
      console.error('Failed to save prompt:', error);
      alert('Failed to save prompt. Please try again.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'escalated':
        return 'warning';
      case 'resolved':
        return 'info';
      default:
        return 'default';
    }
  };

  if (!analytics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Navigation */}
      <AppBar position="static" sx={{ bgcolor: 'background.paper' }}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/dashboard')}
            sx={{ mr: 2 }}
          >
            <ArrowBack />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            Admin Dashboard
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="body2" color="text.secondary">
              {user?.firstName}
            </Typography>
            <UserButton />
          </Stack>
        </Toolbar>
      </AppBar>

      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            System Management
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadData}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>

      {/* Analytics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Conversations
              </Typography>
              <Typography variant="h4">
                {analytics.conversations.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Conversations
              </Typography>
              <Typography variant="h4" color="success.main">
                {analytics.conversations.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Messages
              </Typography>
              <Typography variant="h4">
                {analytics.messages.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Support Actions
              </Typography>
              <Typography variant="h4">
                {analytics.actions.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Conversations */}
      <Paper sx={{ mb: 4 }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">Recent Conversations</Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Customer Email</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Messages</TableCell>
                <TableCell>Created</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {analytics.recent_conversations.map((conversation) => (
                <TableRow key={conversation.id}>
                  <TableCell>{conversation.customer_email}</TableCell>
                  <TableCell>
                    <Chip
                      label={conversation.status}
                      color={getStatusColor(conversation.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{conversation.message_count}</TableCell>
                  <TableCell>
                    {new Date(conversation.created_at).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* System Prompts */}
      <Paper>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">System Prompts</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => {
              setSelectedPrompt(null);
              setPromptForm({ name: '', content: '', description: '', department: 'general' });
              setEditPromptDialog(true);
            }}
          >
            Add Prompt
          </Button>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {prompts.map((prompt) => (
                <TableRow key={prompt.id}>
                  <TableCell>{prompt.name}</TableCell>
                  <TableCell>{prompt.department}</TableCell>
                  <TableCell>{prompt.description}</TableCell>
                  <TableCell>
                    <Chip
                      label={prompt.is_active ? 'Active' : 'Inactive'}
                      color={prompt.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      startIcon={<Edit />}
                      onClick={() => handleEditPrompt(prompt)}
                    >
                      Edit
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Edit Prompt Dialog */}
      <Dialog open={editPromptDialog} onClose={() => setEditPromptDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedPrompt ? 'Edit System Prompt' : 'Add System Prompt'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            variant="outlined"
            value={promptForm.name}
            onChange={(e) => setPromptForm({ ...promptForm, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Department</InputLabel>
            <Select
              value={promptForm.department}
              label="Department"
              onChange={(e) => setPromptForm({ ...promptForm, department: e.target.value })}
            >
              <MenuItem value="general">General</MenuItem>
              <MenuItem value="billing">Billing</MenuItem>
              <MenuItem value="technical">Technical</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            variant="outlined"
            value={promptForm.description}
            onChange={(e) => setPromptForm({ ...promptForm, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Content"
            fullWidth
            multiline
            rows={10}
            variant="outlined"
            value={promptForm.content}
            onChange={(e) => setPromptForm({ ...promptForm, content: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditPromptDialog(false)}>Cancel</Button>
          <Button onClick={handleSavePrompt} variant="contained">
            {selectedPrompt ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
      </Box>
    </Box>
  );
};

export default AdminDashboard;