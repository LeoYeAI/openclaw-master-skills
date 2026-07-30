const { cancelReservation } = require('../lib/api');
const { withRetry } = require('../lib/http');
const { handleSimpleResult } = require('../lib/output');

async function runCancellation(reservationId, profileName) {
  console.log('🗑️ 正在取消预约...');
  const result = await withRetry(
    () => cancelReservation(reservationId, profileName),
    `取消预约 ${reservationId}`
  );
  handleSimpleResult(result, '取消预约成功');
}

module.exports = {
  runCancellation
};
