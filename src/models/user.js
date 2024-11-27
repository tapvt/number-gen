const bcrypt = require('bcryptjs');
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

// Create users table if not exists
const createUsersTable = async () => {
  try {
    const client = await pool.connect();
    try {
      await client.query(`
        CREATE TABLE IF NOT EXISTS users (
          id SERIAL PRIMARY KEY,
          username VARCHAR(50) UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `);
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error creating users table:', error);
  }
};

// Initialize table on module load
createUsersTable();

class User {
  static pool = pool;

  static async create(username, password) {
    try {
      const hashedPassword = await bcrypt.hash(password, 10);
      const client = await this.pool.connect();
      try {
        const result = await client.query(
          'INSERT INTO users (username, password_hash) VALUES ($1, $2) RETURNING id',
          [username, hashedPassword]
        );
        return result.rows[0].id;
      } finally {
        client.release();
      }
    } catch (error) {
      console.error('User creation error:', error);
      throw error;
    }
  }

  static async findByUsername(username) {
    try {
      const client = await this.pool.connect();
      try {
        const result = await client.query(
          'SELECT * FROM users WHERE username = $1',
          [username]
        );
        return result.rows[0];
      } finally {
        client.release();
      }
    } catch (error) {
      console.error('Find user error:', error);
      return null;
    }
  }

  static async verifyPassword(username, password) {
    try {
      const user = await this.findByUsername(username);
      if (!user) return false;
      return await bcrypt.compare(password, user.password_hash);
    } catch (error) {
      console.error('Password verification error:', error);
      return false;
    }
  }
}

module.exports = User;
