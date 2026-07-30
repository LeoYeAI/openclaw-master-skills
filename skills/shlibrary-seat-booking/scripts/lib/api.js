const { CONFIG, AREA_ID_TO_NAME } = require('./config');
const { normalizeSeatNo, normalizeSeatRowLabel } = require('./args');
const { getDailySlots } = require('./slots');
const { request } = require('./http');
const { getAuth, buildAuthHeaders, buildUsePageHeaders } = require('./auth');

function getAreaName(areaId, areaNameOverride = null) {
  return areaNameOverride || AREA_ID_TO_NAME[String(areaId)] || `区域${areaId}`;
}

async function getPeriods(date, profileName = null) {
  const auth = getAuth(profileName);
  if (!auth) throw new Error('未找到认证信息');

  const options = {
    hostname: CONFIG.baseUrl,
    path: `/eastLibReservation/api/period?date=${date}&reservationType=14&libraryId=1`,
    method: 'GET',
    headers: {
      ...CONFIG.defaultHeaders,
      ...buildAuthHeaders(auth)
    }
  };

  return request(options);
}

async function getAreas(profileName = null) {
  const auth = getAuth(profileName);
  if (!auth) throw new Error('未找到认证信息');

  const options = {
    hostname: CONFIG.baseUrl,
    path: `/eastLibReservation/area?floorId=${CONFIG.floorId}`,
    method: 'GET',
    headers: {
      ...CONFIG.defaultHeaders,
      ...buildAuthHeaders(auth)
    }
  };

  return request(options);
}

async function getSeatRows(areaId, profileName = null) {
  const auth = getAuth(profileName);
  if (!auth) throw new Error('未找到认证信息');

  const options = {
    hostname: CONFIG.baseUrl,
    path: `/eastLibReservation/seatReservation/querySeatRow?seatArea=${areaId}`,
    method: 'GET',
    headers: {
      ...CONFIG.defaultHeaders,
      ...buildAuthHeaders(auth)
    }
  };

  return request(options);
}

async function getAvailableSeats(areaId, row, startTime, endTime, profileName = null) {
  const auth = getAuth(profileName);
  if (!auth) throw new Error('未找到认证信息');

  const encodedRow = encodeURIComponent(`${row}排`);
  const encodedStart = encodeURIComponent(startTime);
  const encodedEnd = encodeURIComponent(endTime);

  const options = {
    hostname: CONFIG.baseUrl,
    path: `/eastLibReservation/seatReservation/queryAllAvailableSeatNo?seatArea=${areaId}&seatRow=${encodedRow}&reservationStartTime=${encodedStart}&reservationEndTime=${encodedEnd}`,
    method: 'GET',
    headers: {
      ...CONFIG.defaultHeaders,
      ...buildAuthHeaders(auth)
    }
  };

  return request(options);
}

async function bookSeat(areaId, seatId, startTime, endTime, row, seatNo, profileName = null) {
  const auth = getAuth(profileName);
  if (!auth) throw new Error('未找到认证信息');

  const postData = JSON.stringify({
    areaId,
    floorId: String(CONFIG.floorId),
    reservationStartDate: startTime,
    reservationEndDate: endTime,
    seatId,
    seatReservationType: 2,
    seatRowColumn: `${row}排${seatNo}号`
  });

  const options = {
    hostname: CONFIG.baseUrl,
    path: '/eastLibReservation/seatReservation/reservation',
    method: 'POST',
    headers: {
      ...CONFIG.defaultHeaders,
      'Content-Length': Buffer.byteLength(postData),
      ...buildAuthHeaders(auth)
    }
  };

  return request(options, postData);
}

async function autoAssignSeat(startTime, endTime, profileName = null) {
  const auth = getAuth(profileName);
  if (!auth) throw new Error('未找到认证信息');

  const postData = JSON.stringify({
    areaId: null,
    floorId: String(CONFIG.floorId),
    reservationStartDate: startTime,
    reservationEndDate: endTime,
    seatLabels: [],
    seatReservationType: 1
  });

  const options = {
    hostname: CONFIG.baseUrl,
    path: '/eastLibReservation/seatReservation/reservation',
    method: 'POST',
    headers: {
      ...CONFIG.defaultHeaders,
      'Content-Length': Buffer.byteLength(postData),
      ...buildAuthHeaders(auth)
    }
  };

  return request(options, postData);
}

async function listReservations(status = 0, page = 1, size = 100000, profileName = null) {
  const auth = getAuth(profileName);
  if (!auth) throw new Error('未找到认证信息');

  const postData = JSON.stringify({ status, size, page });
  const options = {
    hostname: CONFIG.baseUrl,
    path: '/eastLibReservation/reservation/myReservationList',
    method: 'POST',
    headers: {
      ...CONFIG.defaultHeaders,
      'Content-Length': Buffer.byteLength(postData),
      ...buildUsePageHeaders(auth)
    }
  };

  return request(options, postData);
}

async function cancelReservation(reservationId, profileName = null) {
  const auth = getAuth(profileName);
  if (!auth) throw new Error('未找到认证信息');

  const options = {
    hostname: CONFIG.baseUrl,
    path: `/eastLibReservation/seatReservation/calcelReservation?reservationId=${encodeURIComponent(reservationId)}`,
    method: 'GET',
    headers: {
      ...CONFIG.defaultHeaders,
      ...buildUsePageHeaders(auth)
    }
  };

  return request(options);
}

async function findCommonAvailableSeatsForArea(date, areaId, profileName = null, areaNameOverride = null) {
  const slots = getDailySlots(date);
  const areaName = getAreaName(areaId, areaNameOverride);
  const rowsResult = await getSeatRows(areaId, profileName);

  if (rowsResult.resultStatus.code !== 0) {
    throw new Error(`查询 ${areaName} 排号失败: ${rowsResult.resultStatus.message || rowsResult.resultStatus.msg || '未知错误'}`);
  }

  const rows = (rowsResult.resultValue || [])
    .map(normalizeSeatRowLabel)
    .filter((row) => /^\d+$/.test(row));

  const seatSetsBySlot = [];

  for (const slot of slots) {
    const fullStartTime = `${date} ${slot.startTime}`;
    const fullEndTime = `${date} ${slot.endTime}`;
    const seatsForSlot = new Set();

    for (const row of rows) {
      const seatsResult = await getAvailableSeats(areaId, row, fullStartTime, fullEndTime, profileName);

      if (seatsResult.resultStatus.code !== 0) {
        throw new Error(`查询 ${areaName} ${row}排 在 ${slot.label} 的可用座位失败: ${seatsResult.resultStatus.message || seatsResult.resultStatus.msg || '未知错误'}`);
      }

      for (const seat of seatsResult.resultValue || []) {
        const seatNo = normalizeSeatNo(seat.seatNo || '');
        seatsForSlot.add(`${row}排${seatNo}号`);
      }
    }

    seatSetsBySlot.push(seatsForSlot);
  }

  const commonSeats = seatSetsBySlot.reduce((acc, currentSet) => {
    if (acc === null) {
      return new Set(currentSet);
    }

    return new Set([...acc].filter((seat) => currentSet.has(seat)));
  }, null);

  return {
    areaId: String(areaId),
    areaName,
    slots,
    rows,
    commonSeats: [...(commonSeats || new Set())].sort((a, b) => {
      const matchA = a.match(/^(\d+)排(\d+)号$/);
      const matchB = b.match(/^(\d+)排(\d+)号$/);
      if (!matchA || !matchB) {
        return a.localeCompare(b, 'zh-Hans-CN');
      }
      const rowDiff = Number(matchA[1]) - Number(matchB[1]);
      if (rowDiff !== 0) {
        return rowDiff;
      }
      return Number(matchA[2]) - Number(matchB[2]);
    })
  };
}

module.exports = {
  getPeriods,
  getAreas,
  getSeatRows,
  getAvailableSeats,
  bookSeat,
  autoAssignSeat,
  listReservations,
  cancelReservation,
  findCommonAvailableSeatsForArea,
  getAreaName
};
