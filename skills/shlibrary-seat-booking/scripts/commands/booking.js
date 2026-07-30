const { DAY_BOOKING_SUBMIT_DELAY_MS } = require('../lib/config');
const { sleep, withRetry } = require('../lib/http');
const { getAvailableSeats, bookSeat, autoAssignSeat } = require('../lib/api');

async function tryBookSpecificSeatForSlot(date, slot, areaId, row, seatNo, profileName) {
  const fullStartTime = `${date} ${slot.startTime}`;
  const fullEndTime = `${date} ${slot.endTime}`;
  const seatsResult = await getAvailableSeats(areaId, row, fullStartTime, fullEndTime, profileName);

  if (seatsResult.resultStatus.code !== 0) {
    return {
      slot,
      success: false,
      message: `查询座位失败: ${seatsResult.resultStatus.message || seatsResult.resultStatus.msg || '未知错误'}`
    };
  }

  const availableSeats = seatsResult.resultValue || [];
  const targetSeat = availableSeats.find((seat) => seat.seatNo === `${seatNo}号`);
  if (!targetSeat) {
    return {
      slot,
      success: false,
      message: `座位 ${row}排${seatNo}号 不可用`
    };
  }

  const result = await withRetry(
    () => bookSeat(areaId, targetSeat.seatId, fullStartTime, fullEndTime, row, seatNo, profileName),
    `${slot.label} 指定座位预约`
  );

  if (result.resultStatus.code === 0) {
    return { slot, success: true, result };
  }

  return {
    slot,
    success: false,
    message: result.resultStatus.msg || result.resultStatus.message || '预约失败',
    result
  };
}

async function tryAutoAssignForSlot(date, slot, profileName) {
  const fullStartTime = `${date} ${slot.startTime}`;
  const fullEndTime = `${date} ${slot.endTime}`;

  const result = await withRetry(
    () => autoAssignSeat(fullStartTime, fullEndTime, profileName),
    `${slot.label} 自动分配预约`
  );

  if (result.resultStatus.code === 0) {
    return { slot, success: true, result };
  }

  return {
    slot,
    success: false,
    message: result.resultStatus.msg || result.resultStatus.message || '预约失败',
    result
  };
}

async function runDayBookingWithDelay(slots, handler) {
  const results = [];

  for (const [index, slot] of slots.entries()) {
    try {
      results.push(await handler(slot));
    } catch (error) {
      results.push({
        slot,
        success: false,
        message: error.message
      });
    }

    if (index < slots.length - 1) {
      console.log(`⏱️ 等待 ${DAY_BOOKING_SUBMIT_DELAY_MS / 1000} 秒后继续下一时段...`);
      await sleep(DAY_BOOKING_SUBMIT_DELAY_MS);
    }
  }

  return results;
}

module.exports = {
  tryBookSpecificSeatForSlot,
  tryAutoAssignForSlot,
  runDayBookingWithDelay
};
