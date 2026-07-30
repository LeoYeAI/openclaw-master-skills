const test = require('node:test');
const assert = require('node:assert/strict');

const auth = require('../scripts/lib/auth');
const api = require('../scripts/lib/api');

const shouldRun = process.env.RUN_LIVE_API_TESTS === '1';
const liveAuthContext = {
  profileName: process.env.SHLIBRARY_TEST_PROFILE || null,
  authFile: process.env.SHLIBRARY_TEST_AUTH_FILE || null
};

let cachedAreas = null;

async function getLiveAreas() {
  if (cachedAreas) {
    return cachedAreas;
  }

  const result = await api.getAreas(liveAuthContext);
  assert.equal(result?.resultStatus?.code, 0, `getAreas failed: ${JSON.stringify(result)}`);
  assert.ok(Array.isArray(result.resultValue), 'getAreas resultValue should be an array');
  assert.ok(result.resultValue.length > 0, 'getAreas returned an empty area list');
  cachedAreas = result.resultValue;
  return cachedAreas;
}

test('live probeAuth succeeds with current auth', { skip: !shouldRun }, async () => {
  const result = await auth.probeAuth(liveAuthContext);
  assert.equal(result.ok, true, `probeAuth failed: ${JSON.stringify(result)}`);
});

test('live getAreas returns seat areas for floor 4', { skip: !shouldRun }, async () => {
  const areas = await getLiveAreas();

  for (const area of areas) {
    assert.equal(typeof area.id, 'number');
    assert.equal(typeof area.areaName, 'string');
    assert.ok(area.areaName.trim().length > 0, 'areaName should not be empty');
    assert.equal(area.areaFloorId, 4);
  }
});

test('live getSeatRows returns row data for the first area', { skip: !shouldRun }, async () => {
  const [firstArea] = await getLiveAreas();
  const result = await api.getSeatRows(firstArea.id, liveAuthContext);

  assert.equal(result?.resultStatus?.code, 0, `getSeatRows failed: ${JSON.stringify(result)}`);
  assert.ok(Array.isArray(result.resultValue), 'getSeatRows resultValue should be an array');
  assert.ok(result.resultValue.length > 0, 'getSeatRows returned no rows');
  assert.match(String(result.resultValue[0].seatRow || ''), /\d+排/);
});

test('live listReservations returns a valid list payload', { skip: !shouldRun }, async () => {
  const result = await api.listReservations(0, 1, 20, liveAuthContext);

  assert.equal(result?.resultStatus?.code, 0, `listReservations failed: ${JSON.stringify(result)}`);
  assert.ok(result.resultValue && typeof result.resultValue === 'object', 'listReservations resultValue should be an object');
  assert.ok(Array.isArray(result.resultValue.content), 'listReservations content should be an array');
  assert.equal(typeof (result.resultValue.totalElements ?? 0), 'number');
});
