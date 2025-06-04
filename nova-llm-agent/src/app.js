require('dotenv').config();
const express = require('express');
const { logger } = require('./utils/logger');
const callHandler = require('./controllers/callHandler');
const gatherProcessor = require('./controllers/gatherProcessor');

const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
  res.json({
    status: 'Server is running',
    endpoints: {
      voice: '/voice (POST)',
      gather: '/gather (POST)'
    }
  });
});

app.post('/voice', callHandler.handleIncomingCall);
app.post('/gather', gatherProcessor.processGather);

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).send('Something went wrong!');
});

// Start server
app.listen(port, () => {
  logger.info(`Server is running on port ${port}`);
}); 