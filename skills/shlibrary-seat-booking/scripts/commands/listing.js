const { listReservations } = require('../lib/api');
const { printReservationList } = require('../lib/output');

async function runListReservations(profileName) {
  console.log('📋 正在查询已有预约...');
  const result = await listReservations(0, 1, 100000, profileName);
  printReservationList(result);
}

module.exports = {
  runListReservations
};
