// Test file with various error handling scenarios

// ❌ Missing error handling - Critical
async function processPayment(orderId, amount) {
  const order = await fetch(`/api/orders/${orderId}`);
  const data = await order.json();
  
  const payment = await chargeCard(data.cardToken, amount);
  
  return payment;
}

// ❌ Missing error handling - High risk
async function verifyToken(token) {
  const decoded = jwt.verify(token, process.env.JWT_SECRET);
  const user = await getUserById(decoded.userId);
  return user;
}

// ⚠️ Weak error handling - Empty catch
async function sendEmail(to, subject, body) {
  try {
    await emailService.send({ to, subject, body });
  } catch (error) {
    // Empty catch - swallowed error!
  }
}

// ⚠️ Weak error handling - Just console.log
async function updateUserProfile(userId, data) {
  try {
    return await db.update('users', userId, data);
  } catch (error) {
    console.log(error);
  }
}

// ✅ Good error handling
async function getUserById(id) {
  try {
    if (!id) {
      throw new ValidationError('User ID is required');
    }
    
    const user = await db.query('SELECT * FROM users WHERE id = $1', [id]);
    
    if (!user) {
      throw new NotFoundError('User not found');
    }
    
    return user;
  } catch (error) {
    if (error instanceof ValidationError || error instanceof NotFoundError) {
      throw error;
    }
    
    logger.error('getUserById failed', { id, error: error.message });
    throw new DatabaseError('Failed to fetch user', { cause: error });
  }
}

// ❌ Risky sync function without error handling
function parseUserInput(json) {
  const data = JSON.parse(json);
  return data.user.name.toUpperCase();
}

module.exports = {
  processPayment,
  verifyToken,
  sendEmail,
  updateUserProfile,
  getUserById,
  parseUserInput
};
