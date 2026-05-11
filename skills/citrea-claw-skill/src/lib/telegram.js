export async function sendTelegram(message) {
  const token  = process.env.TELEGRAM_BOT_TOKEN
  const chatId = process.env.TELEGRAM_CHAT_ID

  if (!token || !chatId) {
    console.warn('⚠️  Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env')
    return
  }

  try {
    const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id:    chatId,
        text:       message,
        parse_mode: 'HTML',
      }),
    })

    if (!res.ok) {
      const err = await res.text()
      console.error('❌ Telegram error:', err)
    }
  } catch (err) {
    console.error('❌ Telegram send failed:', err.message)
  }
}
