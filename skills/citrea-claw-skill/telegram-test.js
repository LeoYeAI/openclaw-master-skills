import 'dotenv/config'
import { sendTelegram } from './src/lib/telegram.js'

await sendTelegram(`
<b>🦞 citrea-claw-skill connected</b>

Telegram alerts are working correctly.
Bot is ready to send arb and pool notifications.
`.trim())

console.log('✅ Test message sent — check your Telegram.')
