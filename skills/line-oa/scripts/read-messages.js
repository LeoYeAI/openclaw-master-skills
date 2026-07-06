/**
 * Read recent messages from the currently open LINE OA chat.
 * Run via browser evaluate on chat.line.biz after opening a chat.
 *
 * Returns: [{ time, text, isCustomer, hasImage }]
 * 
 * This script reads ALL visible messages in the messages panel,
 * up to a maximum of 50 recent messages.
 */
function() {
  const messages = document.querySelectorAll('.chat');
  const result = [];
  
  // Limit to last 50 messages to avoid token overflow
  const recentMessages = Array.from(messages).slice(-50);
  
  for (const msg of recentMessages) {
    // Skip if message has no content
    const textEl = msg.querySelector('.chat-body');
    if (!textEl) continue;
    
    // Extract time
    const timeEl = msg.querySelector('.text-muted.small');
    const time = timeEl?.textContent?.trim() || '';
    
    // Determine if this is a customer message (left side, no .chat-reverse)
    const isCustomer = !msg.classList.contains('chat-reverse');
    
    // Extract text content
    const text = textEl.textContent?.trim() || '';
    
    // Check for images
    const hasImage = !!msg.querySelector('img[alt="Photo"]');
    
    // Skip empty messages
    if (!text && !hasImage) continue;
    
    result.push({
      time,
      text: text.substring(0, 200), // Limit text length
      isCustomer,
      hasImage
    });
  }
  
  return result;
}
