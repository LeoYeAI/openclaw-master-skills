const { AREA_ID_TO_NAME } = require('../lib/config');
const { normalizeAreaId } = require('../lib/args');
const api = require('../lib/api');
const { printCommonAvailabilitySummary } = require('../lib/output');

function getFallbackAreaTargets() {
  return Object.keys(AREA_ID_TO_NAME).map((areaId) => ({
    areaId: String(areaId),
    areaName: AREA_ID_TO_NAME[String(areaId)]
  }));
}

async function resolveAreaTargets(areaInputs, authContext) {
  if (areaInputs.length > 0) {
    return [...new Set(areaInputs.map((input) => normalizeAreaId(input)))].map((areaId) => ({
      areaId: String(areaId),
      areaName: api.getAreaName(areaId)
    }));
  }

  console.log('🧭 未指定区域，正在获取当前可用区域列表...');
  const areasResult = await api.getAreas(authContext);
  if (areasResult?.resultStatus?.code === 0 && Array.isArray(areasResult.resultValue) && areasResult.resultValue.length > 0) {
    return areasResult.resultValue.map((area) => ({
      areaId: String(area.id),
      areaName: String(area.areaName || '').trim() || api.getAreaName(area.id)
    }));
  }

  const message = areasResult?.resultStatus?.message || areasResult?.resultStatus?.msg || '未知错误';
  console.log(`⚠️ 获取区域列表失败，将回退为已知区域: ${message}`);
  return getFallbackAreaTargets();
}

async function runCommonDayAvailability(date, areaInputs, authContext) {
  const areaTargets = await resolveAreaTargets(areaInputs, authContext);

  console.log('🔎 正在查询当天所有时段都可用的座位...');
  const results = [];

  for (const areaTarget of areaTargets) {
    console.log(`- 扫描 ${areaTarget.areaName}...`);
    results.push(await api.findCommonAvailableSeatsForArea(date, areaTarget.areaId, authContext, areaTarget.areaName));
  }

  printCommonAvailabilitySummary(date, results);
}

module.exports = {
  getFallbackAreaTargets,
  resolveAreaTargets,
  runCommonDayAvailability
};
