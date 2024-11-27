const express = require('express');
const router = express.Router();
const Customer = require('../models/customer');
const Order = require('../models/order');
const { requireAuth } = require('../middleware/auth');

router.use(requireAuth);

router.post('/customer', async (req, res) => {
  try {
    const customerNumber = await Customer.generateNumber();
    await Customer.create(customerNumber);

    res.json({
      customer_number: customerNumber,
      success: true
    });
  } catch (error) {
    console.error('Customer generation error:', error);
    res.status(500).json({
      error: 'Failed to generate customer number',
      success: false
    });
  }
});

router.post('/order', async (req, res) => {
  try {
    const orderNumber = await Order.generateNumber();
    await Order.create(orderNumber);

    res.json({
      order_number: orderNumber,
      success: true
    });
  } catch (error) {
    console.error('Order generation error:', error);
    res.status(500).json({
      error: 'Failed to generate order number',
      success: false
    });
  }
});

module.exports = router;
