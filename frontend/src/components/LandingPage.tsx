import React from 'react';
import { motion } from 'framer-motion';
import { useAuth, SignInButton, SignUpButton } from '@clerk/clerk-react';
import { Navigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  Stack,
} from '@mui/material';
import {
  AutoAwesome,
  Speed,
  Security,
  Analytics,
  Support,
  Api,
} from '@mui/icons-material';

const LandingPage: React.FC = () => {
  const { isSignedIn } = useAuth();

  if (isSignedIn) {
    return <Navigate to="/dashboard" replace />;
  }

  const features = [
    {
      icon: <AutoAwesome />,
      title: 'AI-Powered Support',
      description: 'Advanced AI that understands context and provides intelligent responses to customer queries.',
    },
    {
      icon: <Speed />,
      title: 'Lightning Fast',
      description: 'Instant responses with sub-second latency for exceptional customer experience.',
    },
    {
      icon: <Security />,
      title: 'Enterprise Security',
      description: 'Bank-grade security with end-to-end encryption and compliance certifications.',
    },
    {
      icon: <Analytics />,
      title: 'Advanced Analytics',
      description: 'Deep insights into customer interactions and support performance metrics.',
    },
    {
      icon: <Support />,
      title: '24/7 Availability',
      description: 'Round-the-clock support that never sleeps, ensuring customers always get help.',
    },
    {
      icon: <Api />,
      title: 'Easy Integration',
      description: 'Seamless integration with your existing tools and workflows in minutes.',
    },
  ];

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)' }}>
      {/* Navigation */}
      <AppBar position="static" sx={{ background: 'transparent', boxShadow: 'none' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            SupportAI
          </Typography>
          <Stack direction="row" spacing={2}>
            <SignInButton mode="modal">
              <Button
                color="inherit"
                variant="outlined"
                onClick={() => console.log("Sign In button clicked")}
              >Sign In
              </Button>
            </SignInButton>
            <SignUpButton mode="modal">
              <Button
                variant="contained"
                sx={{ bgcolor: '#3b82f6' }}
                onClick={() => console.log("Get Started button clicked")}
              >
                Get Started
              </Button>
            </SignUpButton>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ pt: 8, pb: 8 }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Box textAlign="center" mb={8}>
            <Typography
              variant="h1"
              component="h1"
              sx={{
                fontSize: { xs: '2.5rem', md: '4rem' },
                fontWeight: 'bold',
                background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 3,
              }}
            >
              The Future of
              <br />
              Customer Support
            </Typography>
            <Typography
              variant="h5"
              color="text.secondary"
              sx={{ mb: 4, maxWidth: '600px', mx: 'auto' }}
            >
              Transform your customer support with AI-powered conversations that understand,
              learn, and deliver exceptional experiences at scale.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
              <SignUpButton mode="modal">
                <Button
                  variant="contained"
                  size="large"
                  sx={{
                    bgcolor: '#3b82f6',
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    '&:hover': { bgcolor: '#2563eb' },
                  }}
                >
                  Start Free Trial
                </Button>
              </SignUpButton>
              <Button
                variant="outlined"
                size="large"
                sx={{ px: 4, py: 1.5, fontSize: '1.1rem' }}
              >
                Watch Demo
              </Button>
            </Stack>
          </Box>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <Typography
            variant="h3"
            component="h2"
            textAlign="center"
            sx={{ mb: 6, fontWeight: 'bold' }}
          >
            Why Choose SupportAI?
          </Typography>
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={6} lg={4} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  whileHover={{ y: -5 }}
                >
                  <Card
                    sx={{
                      height: '100%',
                      background: 'rgba(255, 255, 255, 0.05)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      '&:hover': {
                        background: 'rgba(255, 255, 255, 0.08)',
                        transform: 'translateY(-4px)',
                        transition: 'all 0.3s ease',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 3 }}>
                      <Box
                        sx={{
                          color: '#3b82f6',
                          mb: 2,
                          '& svg': { fontSize: '2.5rem' },
                        }}
                      >
                        {feature.icon}
                      </Box>
                      <Typography variant="h6" component="h3" sx={{ mb: 2, fontWeight: 'bold' }}>
                        {feature.title}
                      </Typography>
                      <Typography color="text.secondary">
                        {feature.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <Box
            textAlign="center"
            sx={{
              mt: 12,
              p: 6,
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
              borderRadius: 4,
              border: '1px solid rgba(59, 130, 246, 0.2)',
            }}
          >
            <Typography variant="h4" component="h2" sx={{ mb: 3, fontWeight: 'bold' }}>
              Ready to Transform Your Support?
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
              Join thousands of companies already using SupportAI to deliver exceptional customer experiences.
            </Typography>
            <SignUpButton mode="modal">
              <Button
                variant="contained"
                size="large"
                sx={{
                  bgcolor: '#3b82f6',
                  px: 6,
                  py: 2,
                  fontSize: '1.2rem',
                  '&:hover': { bgcolor: '#2563eb' },
                }}
              >
                Get Started Today
              </Button>
            </SignUpButton>
          </Box>
        </motion.div>
      </Container>
    </Box>
  );
};

export default LandingPage;