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

class Order {
  static pool = pool;

  static async generateNumber() {
    try {
      const client = await this.pool.connect();
      try {
        // Get the current year's last two digits
        const year = new Date().getFullYear().toString().slice(-2);

        // Get the next sequence number for this year
        const result = await client.query(`
          WITH updated_sequence AS (
            INSERT INTO order_sequences (year, last_sequence)
            VALUES ($1::text, COALESCE(
              (SELECT last_sequence FROM order_sequences WHERE year = $1::text), 0
            ) + 1)
            ON CONFLICT (year) DO UPDATE
            SET last_sequence = order_sequences.last_sequence + 1
            RETURNING last_sequence
          )
          SELECT last_sequence FROM updated_sequence
        `, [year]);

        const sequenceNumber = result.rows[0].last_sequence;
        return `O${year}-${sequenceNumber.toString().padStart(7, '0')}`;
      } finally {
        client.release();
      }
    } catch (error) {
      console.error('Order number generation error:', error);
      throw error;
    }
  }

  static async create(orderNumber) {
    try {
      const client = await this.pool.connect();
      try {
        const result = await client.query(
          'INSERT INTO orders (order_number) VALUES ($1) RETURNING id',
          [orderNumber]
        );
        return {
          id: result.rows[0].id,
          orderNumber
        };
      } finally {
        client.release();
      }
    } catch (error) {
      console.error('Order creation error:', error);
      throw error;
    }
  }

  static async findByCustomerNumber(customerNumber) {
    try {
      const client = await this.pool.connect();
      try {
        const result = await client.query(
          'SELECT * FROM orders WHERE customer_number = $1',
          [customerNumber]
        );
        return result.rows.map(row => ({
          ...row,
          orderDetails: row.order_details ? JSON.parse(row.order_details) : null
        }));
      } finally {
        client.release();
      }
    } catch (error) {
      console.error('Find order error:', error);
      return null;
    }
  }

  // Create orders table and sequences table if not exists
  static async createOrdersTables() {
    try {
      const client = await this.pool.connect();
      try {
        // Orders table
        await client.query(`
          CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_number VARCHAR(50) UNIQUE NOT NULL,
            customer_number VARCHAR(50),
            order_details JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          )
        `);

        // Sequences table to track incremental numbers per year
        await client.query(`
          CREATE TABLE IF NOT EXISTS order_sequences (
            year VARCHAR(2) PRIMARY KEY,
            last_sequence INTEGER NOT NULL DEFAULT 0
          )
        `);
      } finally {
        client.release();
      }
    } catch (error) {
      console.error('Error creating orders tables:', error);
    }
  }
}

// Initialize tables on module load
Order.createOrdersTables();

module.exports = Order;
