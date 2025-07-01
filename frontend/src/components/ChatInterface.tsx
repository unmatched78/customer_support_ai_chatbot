import React, { useState, useEffect, useRef } from 'react';
import { useUser, UserButton } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  Avatar,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  AppBar,
  Toolbar,
  IconButton,
  Stack
} from '@mui/material';
import { Send, Person, SmartToy, ArrowBack } from '@mui/icons-material';
import axios from 'axios';

interface Message {
  id: number;
  content: string;
  sender: string;
  timestamp: string;
  metadata?: any;
}

interface ChatSession {
  sessionId: string | null;
  isActive: boolean;
}

const ChatInterface: React.FC = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [session, setSession] = useState<ChatSession>({ sessionId: null, isActive: false });
  const [customerInfo, setCustomerInfo] = useState({ 
    email: user?.primaryEmailAddress?.emailAddress || '', 
    name: user?.fullName || '' 
  });
  const [showStartDialog, setShowStartDialog] = useState(true);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startChat = async () => {
    if (!customerInfo.email || !customerInfo.name) {
      alert('Please enter your email and name');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post('/api/v1/chat/start', {
        customer_email: customerInfo.email,
        customer_name: customerInfo.name
      });

      setSession({
        sessionId: response.data.session_id,
        isActive: true
      });
      setShowStartDialog(false);
      
      // Load conversation history
      await loadHistory(response.data.session_id);
    } catch (error) {
      console.error('Failed to start chat:', error);
      alert('Failed to start chat. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async (sessionId: string) => {
    try {
      const response = await axios.get(`/api/v1/chat/history/${sessionId}`);
      setMessages(response.data);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !session.sessionId) return;

    const userMessage = inputMessage;
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post('/api/v1/chat/message', {
        session_id: session.sessionId,
        content: userMessage
      });

      // Reload conversation history to get the latest messages
      await loadHistory(session.sessionId);
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const getMessageIcon = (sender: string) => {
    switch (sender) {
      case 'customer':
        return <Person />;
      case 'ai':
        return <SmartToy />;
      default:
        return <SmartToy />;
    }
  };

  const getMessageColor = (sender: string) => {
    switch (sender) {
      case 'customer':
        return 'primary';
      case 'ai':
        return 'secondary';
      default:
        return 'default';
    }
  };

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
            Customer Support Chat
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
        <Dialog open={showStartDialog} onClose={() => {}} maxWidth="sm" fullWidth>
        <DialogTitle>Start Customer Support Chat</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Your Email"
            type="email"
            fullWidth
            variant="outlined"
            value={customerInfo.email}
            onChange={(e) => setCustomerInfo({ ...customerInfo, email: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Your Name"
            type="text"
            fullWidth
            variant="outlined"
            value={customerInfo.name}
            onChange={(e) => setCustomerInfo({ ...customerInfo, name: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={startChat} disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Start Chat'}
          </Button>
        </DialogActions>
      </Dialog>

      {session.isActive && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Customer Support Chat
          </Typography>
          
          <Paper elevation={3} sx={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ flexGrow: 1, overflow: 'auto', p: 1 }}>
              <List>
                {messages.map((message) => (
                  <ListItem key={message.id} alignItems="flex-start">
                    <Avatar sx={{ mr: 2, bgcolor: getMessageColor(message.sender) }}>
                      {getMessageIcon(message.sender)}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle2">
                              {message.sender === 'customer' ? customerInfo.name : 'AI Assistant'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(message.timestamp).toLocaleTimeString()}
                            </Typography>
                          </Box>
                        }
                        secondary={message.content}
                      />
                      {message.metadata?.confidence && (
                        <Chip
                          label={`Confidence: ${(message.metadata.confidence * 100).toFixed(0)}%`}
                          size="small"
                          color={message.metadata.confidence > 0.8 ? 'success' : 'warning'}
                          sx={{ mt: 1 }}
                        />
                      )}
                      {message.metadata?.suggested_actions && message.metadata.suggested_actions.length > 0 && (
                        <Box sx={{ mt: 1 }}>
                          {message.metadata.suggested_actions.map((action: string, index: number) => (
                            <Chip
                              key={index}
                              label={action.replace('_', ' ')}
                              size="small"
                              variant="outlined"
                              sx={{ mr: 1 }}
                            />
                          ))}
                        </Box>
                      )}
                    </Box>
                  </ListItem>
                ))}
              </List>
              <div ref={messagesEndRef} />
            </Box>
            
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={3}
                  placeholder="Type your message..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading}
                />
                <Button
                  variant="contained"
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || loading}
                  sx={{ minWidth: 'auto', px: 2 }}
                >
                  {loading ? <CircularProgress size={20} /> : <Send />}
                </Button>
              </Box>
            </Box>
          </Paper>
        </Box>
      )}
      </Box>
    </Box>
  );
};

export default ChatInterface;