#!/usr/bin/env node
const { Pool } = require('pg');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// PostgreSQL Connection Pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
});

async function wipeDatabase() {
  const client = await pool.connect();

  try {
    // Drop tables in the correct order to avoid foreign key constraints
    await client.query('DROP TABLE IF EXISTS orders');
    await client.query('DROP TABLE IF EXISTS customers');
    await client.query('DROP TABLE IF EXISTS users');

    console.log('Database wiped successfully.');
  } catch (error) {
    console.error('Error wiping database:', error);
  } finally {
    client.release();
    await pool.end();
  }
}

// Run the wipe function
wipeDatabase();
