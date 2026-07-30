const test = require('node:test');
const assert = require('node:assert/strict');

const api = require('../scripts/lib/api');
const availability = require('../scripts/commands/availability');

function withMockedApi(overrides, fn) {
  const original = {};

  for (const [key, value] of Object.entries(overrides)) {
    original[key] = api[key];
    api[key] = value;
  }

  const restore = () => {
    for (const [key, value] of Object.entries(original)) {
      api[key] = value;
    }
  };

  try {
    const result = fn();
    if (result && typeof result.then === 'function') {
      return result.finally(restore);
    }
    restore();
    return result;
  } catch (error) {
    restore();
    throw error;
  }
}

test('resolveAreaTargets normalizes and de-duplicates explicit areas', async () => {
  const result = await availability.resolveAreaTargets(['南区', '5', '北区'], {});
  assert.deepEqual(result, [
    { areaId: '5', areaName: '南区' },
    { areaId: '4', areaName: '北区' }
  ]);
});

test('resolveAreaTargets uses live area list when no area is specified', async () => {
  await withMockedApi({
    getAreas: async () => ({
      resultStatus: { code: 0, message: '操作成功。' },
      resultValue: [
        { id: 6, areaName: '特藏区' },
        { id: 7, areaName: '报刊区' }
      ]
    }),
    getAreaName: (areaId) => `区域${areaId}`
  }, async () => {
    const result = await availability.resolveAreaTargets([], { profileName: 'user1' });
    assert.deepEqual(result, [
      { areaId: '6', areaName: '特藏区' },
      { areaId: '7', areaName: '报刊区' }
    ]);
  });
});

test('resolveAreaTargets falls back to known areas when live query fails', async () => {
  await withMockedApi({
    getAreas: async () => ({
      resultStatus: { code: 101, message: '获取用户信息时出现异常' },
      resultValue: null
    })
  }, async () => {
    const result = await availability.resolveAreaTargets([], {});
    assert.deepEqual(result, [
      { areaId: '2', areaName: '东区' },
      { areaId: '3', areaName: '西区' },
      { areaId: '4', areaName: '北区' },
      { areaId: '5', areaName: '南区' }
    ]);
  });
});
