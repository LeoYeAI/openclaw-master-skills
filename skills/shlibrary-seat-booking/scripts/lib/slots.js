const { SLOT_SCHEDULES, DAY_BOOKING_ORDER } = require('./config');

function getWeekday(date) {
  const [year, month, day] = date.split('-').map(Number);
  return new Date(Date.UTC(year, month - 1, day)).getUTCDay();
}

function resolveTimeSlot(date, slotLabel) {
  const normalizedSlot = String(slotLabel || '').trim();
  const isMonday = getWeekday(date) === 1;
  const schedule = isMonday ? SLOT_SCHEDULES.monday : SLOT_SCHEDULES.regular;
  const slot = schedule[normalizedSlot];

  if (!slot) {
    const validLabels = Object.keys(schedule).join(' / ');
    throw new Error(`${date} 可用时段为: ${validLabels}。你提供的是: ${normalizedSlot || '(空)'}`);
  }

  return {
    label: normalizedSlot,
    startTime: slot[0],
    endTime: slot[1]
  };
}

function getDailySlots(date) {
  const isMonday = getWeekday(date) === 1;
  const schedule = isMonday ? SLOT_SCHEDULES.monday : SLOT_SCHEDULES.regular;

  return DAY_BOOKING_ORDER
    .filter((label) => schedule[label])
    .map((label) => ({
      label,
      startTime: schedule[label][0],
      endTime: schedule[label][1]
    }));
}

module.exports = {
  getWeekday,
  resolveTimeSlot,
  getDailySlots
};
