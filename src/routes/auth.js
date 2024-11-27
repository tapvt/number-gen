const express = require('express');
const router = express.Router();
const User = require('../models/user');
const path = require('path');

router.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, '../../public/login.html'));
});

router.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, '../../public/register.html'));
});

router.post('/register', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Check if user already exists
    const existingUser = await User.findByUsername(username);
    if (existingUser) {
      return res.status(400).json({ error: 'Username already exists' });
    }

    // Create new user
    const userId = await User.create(username, password);

    res.status(201).json({ message: 'Registration successful', userId });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Registration failed' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Verify user credentials
    const isValidUser = await User.verifyPassword(username, password);

    if (isValidUser) {
      // Set user session
      req.session.user = { username };
      res.json({ message: 'Login successful', redirect: '/' });
    } else {
      res.status(401).json({ error: 'Invalid username or password' });
    }
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

router.get('/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Could not log out' });
    }
    res.redirect('/auth/login');
  });
});

module.exports = router;
