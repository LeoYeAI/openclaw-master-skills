const test = require('node:test');
const assert = require('node:assert/strict');

const { getWeekday, resolveTimeSlot, getDailySlots } = require('../scripts/lib/slots');

test('getWeekday returns Monday for 2026-03-23', () => {
  assert.equal(getWeekday('2026-03-23'), 1);
});

test('resolveTimeSlot uses Monday schedule', () => {
  assert.deepEqual(resolveTimeSlot('2026-03-23', '下午'), {
    label: '下午',
    startTime: '13:45:00',
    endTime: '16:45:00'
  });
});

test('resolveTimeSlot rejects unavailable Monday morning slot', () => {
  assert.throws(
    () => resolveTimeSlot('2026-03-23', '上午'),
    /可用时段为: 下午 \/ 晚上/
  );
});

test('getDailySlots returns configured order for regular day', () => {
  assert.deepEqual(getDailySlots('2026-03-24').map((slot) => slot.label), ['下午', '晚上', '上午']);
});

test('getDailySlots omits morning on Monday', () => {
  assert.deepEqual(getDailySlots('2026-03-23').map((slot) => slot.label), ['下午', '晚上']);
});
