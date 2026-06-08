/**
 * Smart Email Agent v3 — OpenClaw Bootstrap Hook
 * Inyecta estado de presupuesto, modo activo y learnings pendientes.
 */
const fs   = require('fs');
const path = require('path');
const WS   = path.join(process.env.HOME, '.openclaw', 'workspace');

function getBudgetInfo() {
  const f = path.join(WS, 'budget_tracker.json');
  try {
    if (!fs.existsSync(f)) return '⚠️  budget_tracker.json no encontrado. Ejecuta: python3 scripts/init_orchestrator.py';
    const d   = JSON.parse(fs.readFileSync(f, 'utf8'));
    const pct = Math.round(d.spent_usd / d.budget_usd * 100);
    const proj = (d.spent_usd / new Date().getDate() * 31).toFixed(3);
    let mode, model, restriction = null;
    if      (pct >= 95) { mode = '🔴 EMERGENCIA';    model = 'ninguno — cero IA';               restriction = 'CRITICO: No llamar a Anthropic API. Solo gog + reglas locales.'; }
    else if (pct >= 80) { mode = '🟠 AHORRO FUERTE'; model = 'claude-haiku-4-5-20251001 forzado'; restriction = 'ACTIVO: Solo Haiku. Sin borradores. Batch >= 20.'; }
    else if (pct >= 60) { mode = '🟡 AHORRO LEVE';   model = 'Haiku preferido';                 restriction = 'AVISO: Max 2 borradores/sesión.'; }
    else                { mode = '✅ NORMAL';          model = 'Haiku → clasificar | Sonnet → borradores prio≥8'; }
    const lines = [
      '## Smart Email Agent — Contexto',
      `Presupuesto: $${d.spent_usd.toFixed(3)} / $${d.budget_usd.toFixed(2)} (${pct}%) | Proyección: $${proj} | Mes: ${d.month}`,
      `Modo: ${mode} | Modelo: ${model}`,
    ];
    if (restriction) lines.push(`> ⚡ ${restriction}`);
    return lines.join('\n');
  } catch (e) { return `⚠️  Error leyendo presupuesto: ${e.message}`; }
}

function getPendingLearnings() {
  const f = path.join(WS, '.learnings', 'LEARNINGS.md');
  try {
    if (!fs.existsSync(f)) return null;
    const n = (fs.readFileSync(f, 'utf8').match(/\*\*Status\*\*: pending/g) || []).length;
    return n > 0 ? `Learnings pendientes: ${n} — revisar al cerrar sesión.` : null;
  } catch { return null; }
}

const handler = async (event) => {
  if (!event?.context || !Array.isArray(event.context.bootstrapFiles)) return;
  if (event.type !== 'agent' || event.action !== 'bootstrap') return;
  if ((event.sessionKey || '').includes(':subagent:')) return;

  const parts = [getBudgetInfo()];
  const l = getPendingLearnings();
  if (l) parts.push(l);
  parts.push('Lazy loading: NO cargar los 6 skills de email por separado. Este skill los fusiona todos.');

  event.context.bootstrapFiles.push({
    path: 'SMART_EMAIL_CTX.md',
    content: parts.join('\n'),
    virtual: true,
  });
};

module.exports = handler;
module.exports.default = handler;
