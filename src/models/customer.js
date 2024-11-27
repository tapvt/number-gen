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

class Customer {
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
            INSERT INTO customer_sequences (year, last_sequence)
            VALUES ($1::text, COALESCE(
              (SELECT last_sequence FROM customer_sequences WHERE year = $1::text), 0
            ) + 1)
            ON CONFLICT (year) DO UPDATE
            SET last_sequence = customer_sequences.last_sequence + 1
            RETURNING last_sequence
          )
          SELECT last_sequence FROM updated_sequence
        `, [year]);

        const sequenceNumber = result.rows[0].last_sequence;
        return `C${year}-${sequenceNumber.toString().padStart(7, '0')}`;
      } finally {
        client.release();
      }
    } catch (error) {
      console.error('Customer number generation error:', error);
      throw error;
    }
  }

  static async create(customerNumber) {
    try {
      const client = await this.pool.connect();
      try {
        const result = await client.query(
          'INSERT INTO customers (customer_number) VALUES ($1) RETURNING id',
          [customerNumber]
        );
        return {
          id: result.rows[0].id,
          customerNumber
        };
      } finally {
        client.release();
      }
    } catch (error) {
      console.error('Customer creation error:', error);
      throw error;
    }
  }

  static async findByCustomerNumber(customerNumber) {
    try {
      const client = await this.pool.connect();
      try {
        const result = await client.query(
          'SELECT * FROM customers WHERE customer_number = $1',
          [customerNumber]
        );
        return result.rows[0];
      } finally {
        client.release();
      }
    } catch (error) {
      console.error('Find customer error:', error);
      return null;
    }
  }

  // Create customers table and sequences table if not exists
  static async createCustomersTables() {
    try {
      const client = await this.pool.connect();
      try {
        // Customers table
        await client.query(`
          CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            customer_number VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          )
        `);

        // Sequences table to track incremental numbers per year
        await client.query(`
          CREATE TABLE IF NOT EXISTS customer_sequences (
            year VARCHAR(2) PRIMARY KEY,
            last_sequence INTEGER NOT NULL DEFAULT 0
          )
        `);
      } finally {
        client.release();
      }
    } catch (error) {
      console.error('Error creating customers tables:', error);
    }
  }
}

// Initialize tables on module load
Customer.createCustomersTables();

module.exports = Customer;
