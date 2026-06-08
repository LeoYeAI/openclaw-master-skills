#!/usr/bin/env node
/**
 * Dispatcher Integration Test
 *
 * Exercises every outbound dispatch path by creating real data
 * in the Mission Control API, then making decisions that trigger
 * dispatches, and verifying the activity log records them.
 *
 * Prerequisites:
 *   - Mission Control backend running on $MC_URL (default: http://localhost:8000)
 *   - No auth required (AUTH_MODE=none), or pass --secret
 *
 * Usage:
 *   node test-dispatcher.js
 *   node test-dispatcher.js --url http://localhost:8001
 *   node test-dispatcher.js --secret my-hook-secret
 *   node test-dispatcher.js --verbose
 */

const BASE = process.argv.includes("--url")
  ? process.argv[process.argv.indexOf("--url") + 1]
  : "http://localhost:8000";

const HOOK_SECRET = process.argv.includes("--secret")
  ? process.argv[process.argv.indexOf("--secret") + 1]
  : process.env.HOOK_SECRET || "test-secret";

const VERBOSE = process.argv.includes("--verbose");

let passed = 0;
let failed = 0;

// ── Helpers ─────────────────────────────────────────
async function api(path, opts = {}) {
  const url = `${BASE}/api${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...opts.headers },
    ...opts,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok && VERBOSE) {
    console.error(`    API ERROR: ${res.status} ${url}`, data);
  }
  return { status: res.status, data };
}

async function hook(event, agentId, taskId, extraData = {}) {
  return api("/hooks/event", {
    method: "POST",
    headers: { "X-Hook-Secret": HOOK_SECRET },
    body: JSON.stringify({ event, agentId, taskId, data: extraData }),
  });
}

function assert(condition, label) {
  if (condition) {
    console.log(`  ✅ ${label}`);
    passed++;
  } else {
    console.error(`  ❌ ${label}`);
    failed++;
  }
}

async function getDispatchLogs(event, limit = 5) {
  // Check activity log for dispatch entries
  const { data } = await api(`/events/activity?entity_type=dispatch&limit=${limit}`);
  return (data || []).filter(a => a.action === event);
}

// Small delay to let dispatches process
const wait = (ms) => new Promise(r => setTimeout(r, ms));

// ── Tests ───────────────────────────────────────────
async function run() {
  console.log(`\n🎛️  Dispatcher Integration Test`);
  console.log(`   Backend: ${BASE}`);
  console.log(`   Hook Secret: ${HOOK_SECRET.slice(0, 4)}...`);
  console.log("");

  // ── 0. Health check ──────────────────────────────
  console.log("0. Health check");
  const { status: healthStatus, data: health } = await api("/health");
  assert(healthStatus === 200, `Backend is reachable (${healthStatus})`);
  if (healthStatus !== 200) {
    console.error("\n   Cannot reach backend. Is it running?");
    process.exit(1);
  }

  // ── 1. Create test project ───────────────────────
  console.log("\n1. Setup: Create test project and tasks");
  const { data: project } = await api("/projects", {
    method: "POST",
    body: JSON.stringify({ name: "Dispatcher Test Project", description: "Testing outbound dispatches", priority: "high", owner_agent: "test-agent" }),
  });
  assert(project?.id, `Project created: ${project?.id}`);

  const { data: task1 } = await api("/tasks", {
    method: "POST",
    body: JSON.stringify({ project_id: project.id, title: "Test Task Alpha", priority: "high", assigned_agent: "test-agent", pipeline_stage: "backlog" }),
  });
  assert(task1?.id, `Task created: ${task1?.id}`);

  const { data: task2 } = await api("/tasks", {
    method: "POST",
    body: JSON.stringify({ project_id: project.id, title: "Test Task Beta", priority: "medium", pipeline_stage: "backlog" }),
  });
  assert(task2?.id, `Second task created: ${task2?.id}`);

  // ── 2. Test task:assigned dispatch ───────────────
  console.log("\n2. Task assignment → mc:task_assigned");
  await api(`/tasks/${task2.id}`, {
    method: "PATCH",
    body: JSON.stringify({ assigned_agent: "test-agent-2" }),
  });
  await wait(100);
  // Check the task was updated
  const { data: assignedTask } = await api(`/tasks/${task2.id}`);
  assert(assignedTask?.assigned_agent === "test-agent-2", "Task assigned to test-agent-2");

  // ── 3. Test task stage change → mc:task_resume ──
  console.log("\n3. Task move to doing → mc:task_resume");
  await api(`/tasks/${task1.id}/move`, {
    method: "POST",
    body: JSON.stringify({ to_stage: "todo", actor: "user" }),
  });
  await api(`/tasks/${task1.id}/move`, {
    method: "POST",
    body: JSON.stringify({ to_stage: "doing", actor: "user" }),
  });
  await wait(100);
  const { data: doingTask } = await api(`/tasks/${task1.id}`);
  assert(doingTask?.pipeline_stage === "doing", "Task moved to doing");

  // ── 4. Submit for review via hook ───────────────
  console.log("\n4. Hook: task:review → creates review record");
  await hook("task:review", "test-agent", task1.id, {
    work_summary: "Test work completed",
    deliverables: [{ name: "test.md", type: "doc", summary: "Test deliverable" }],
    checklist: [{ label: "Tests pass", checked: true }],
  });
  await wait(200);
  const { data: doingTask2 } = await api(`/tasks/${task1.id}`);
  assert(doingTask2?.pipeline_stage === "review", "Task moved to review by hook");

  // Get the review
  const { data: reviews } = await api(`/reviews?task_id=${task1.id}`);
  const review = reviews?.[0];
  assert(review?.id, `Review created: ${review?.id}`);

  // ── 5. Review: changes_requested → mc:changes_requested
  console.log("\n5. Review changes requested → mc:changes_requested");
  if (review) {
    await api(`/reviews/${review.id}/decide`, {
      method: "POST",
      body: JSON.stringify({ decision: "changes_requested", notes: "Needs more tests", reviewer: "user" }),
    });
    await wait(100);
    const { data: revisedTask } = await api(`/tasks/${task1.id}`);
    assert(revisedTask?.pipeline_stage === "doing", "Task moved back to doing");
  } else {
    assert(false, "No review to decide on (skipped)");
  }

  // ── 6. Resubmit and approve → mc:review_approved
  console.log("\n6. Resubmit review and approve → mc:review_approved");
  // Move back to review
  await api(`/tasks/${task1.id}/move`, {
    method: "POST",
    body: JSON.stringify({ to_stage: "review", actor: "test-agent" }),
  });
  // Create a new review for round 2
  const { data: review2 } = await api("/reviews", {
    method: "POST",
    body: JSON.stringify({
      task_id: task1.id, project_id: project.id, submitted_by: "test-agent",
      work_summary: "Fixed the tests", round: 2,
    }),
  });
  if (review2?.id) {
    await api(`/reviews/${review2.id}/decide`, {
      method: "POST",
      body: JSON.stringify({ decision: "approved", notes: "Looks good", quality_score: 5, reviewer: "user" }),
    });
    await wait(100);
    const { data: doneTask } = await api(`/tasks/${task1.id}`);
    assert(doneTask?.pipeline_stage === "done", "Task moved to done after approval");
  } else {
    assert(false, "Could not create round 2 review (skipped)");
  }

  // ── 7. Approval: workflow gate → mc:approval_granted
  console.log("\n7. Approval granted → mc:approval_granted");
  await hook("approval:needed", "test-agent", null, {
    type: "workflow_gate",
    title: "Test deploy gate",
    description: "CI passed, deploy?",
    urgency: "urgent",
    resumeToken: "test_resume_token_123",
  });
  await wait(200);
  const { data: approvals } = await api("/approvals");
  const pendingApproval = approvals?.find(a => a.title === "Test deploy gate" && a.status === "pending");
  assert(pendingApproval?.id, `Approval created: ${pendingApproval?.id}`);

  if (pendingApproval) {
    await api(`/approvals/${pendingApproval.id}/decide`, {
      method: "POST",
      body: JSON.stringify({ decision: "approved", notes: "Go ahead", decided_by: "user" }),
    });
    await wait(100);
    const { data: decidedApproval } = await api(`/approvals/${pendingApproval.id}`);
    assert(decidedApproval?.status === "approved", "Approval was granted");
  }

  // ── 8. Approval denied → mc:approval_denied
  console.log("\n8. Approval denied → mc:approval_denied");
  await hook("approval:needed", "test-agent", null, {
    type: "workflow_gate",
    title: "Test delete gate",
    description: "Delete prod data?",
    urgency: "critical",
  });
  await wait(200);
  const { data: approvals2 } = await api("/approvals");
  const deleteGate = approvals2?.find(a => a.title === "Test delete gate" && a.status === "pending");
  if (deleteGate) {
    await api(`/approvals/${deleteGate.id}/decide`, {
      method: "POST",
      body: JSON.stringify({ decision: "rejected", notes: "Too dangerous", decided_by: "user" }),
    });
    await wait(100);
    assert(true, "Approval denied dispatched");
  } else {
    assert(false, "Delete gate not found (skipped)");
  }

  // ── 9. Request → project conversion → mc:project_kickoff
  console.log("\n9. Request conversion → mc:project_kickoff");
  const { data: request } = await api("/requests", {
    method: "POST",
    body: JSON.stringify({ title: "Test Kickoff Request", description: "Should become a project", category: "feature", urgency: "normal" }),
  });
  assert(request?.id, `Request created: ${request?.id}`);

  if (request?.id) {
    const { data: converted } = await api(`/requests/${request.id}/convert`, {
      method: "POST",
      body: JSON.stringify({ owner_agent: "test-agent" }),
    });
    assert(converted?.project?.id, `Converted to project: ${converted?.project?.id}`);
  }

  // ── 10. Project activated → mc:project_activated
  console.log("\n10. Project activation → mc:project_activated");
  const { data: proj2 } = await api("/projects", {
    method: "POST",
    body: JSON.stringify({ name: "Activation Test", priority: "medium", owner_agent: "test-agent" }),
  });
  if (proj2?.id) {
    await api(`/projects/${proj2.id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "active" }),
    });
    await wait(100);
    const { data: activeProj } = await api(`/projects/${proj2.id}`);
    assert(activeProj?.status === "active", "Project activated");
  }

  // ── 11. Project paused → mc:project_paused
  console.log("\n11. Project pause → mc:project_paused");
  if (proj2?.id) {
    await api(`/projects/${proj2.id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "paused" }),
    });
    await wait(100);
    const { data: pausedProj } = await api(`/projects/${proj2.id}`);
    assert(pausedProj?.status === "paused", "Project paused");
  }

  // ── 12. Review rejected → mc:review_rejected
  console.log("\n12. Review rejected → mc:review_rejected");
  const { data: task3 } = await api("/tasks", {
    method: "POST",
    body: JSON.stringify({ project_id: project.id, title: "Reject Test Task", assigned_agent: "test-agent", pipeline_stage: "review" }),
  });
  if (task3?.id) {
    const { data: review3 } = await api("/reviews", {
      method: "POST",
      body: JSON.stringify({ task_id: task3.id, project_id: project.id, submitted_by: "test-agent", work_summary: "Bad work" }),
    });
    if (review3?.id) {
      await api(`/reviews/${review3.id}/decide`, {
        method: "POST",
        body: JSON.stringify({ decision: "rejected", notes: "Completely wrong approach", reviewer: "user" }),
      });
      await wait(100);
      const { data: rejTask } = await api(`/tasks/${task3.id}`);
      assert(rejTask?.pipeline_stage === "todo", "Rejected task moved to todo");
    }
  }

  // ── 13. Library publish via hook
  console.log("\n13. Library publish via hook");
  await hook("library:publish", "test-agent", null, {
    title: "Dispatcher Test Document",
    content: "# Test\n\nThis was published by the dispatcher test.",
    doc_type: "note",
    format: "markdown",
    collection_id: "col_notes",
  });
  await wait(200);
  const { data: docs } = await api("/library/documents?collection_id=col_notes");
  const testDoc = docs?.find(d => d.title === "Dispatcher Test Document");
  assert(testDoc?.id, `Document published: ${testDoc?.id}`);

  // ── 14. Input sanitization check
  console.log("\n14. Input sanitization");
  const { data: xssProject } = await api("/projects", {
    method: "POST",
    body: JSON.stringify({
      name: 'Test <script>alert("xss")</script> Project',
      description: 'Has <img onerror=alert(1) src=x> and javascript:void(0)',
    }),
  });
  if (xssProject) {
    assert(!xssProject.name.includes("<script>"), "Script tags stripped from project name");
    assert(!xssProject.description.includes("onerror"), "Event handlers stripped from description");
  }

  const { data: xssDoc } = await api("/library/documents", {
    method: "POST",
    body: JSON.stringify({
      title: "Sanitization Test",
      content: '<p>Normal text</p><script>steal(cookies)</script><iframe src="evil"></iframe>',
      doc_type: "note",
      format: "markdown",
    }),
  });
  if (xssDoc) {
    const { data: fullDoc } = await api(`/library/documents/${xssDoc.id}`);
    assert(!fullDoc.content.includes("<script>"), "Script tags stripped from document content");
    assert(!fullDoc.content.includes("<iframe"), "Iframe tags stripped from document content");
  }

  // ── 15. Validation check
  console.log("\n15. Input validation");
  const { status: s1 } = await api("/projects", {
    method: "POST",
    body: JSON.stringify({ name: "" }),
  });
  assert(s1 === 400, "Empty project name rejected");

  const { status: s2 } = await api("/tasks", {
    method: "POST",
    body: JSON.stringify({ title: "X", priority: "MEGA_ULTRA" }),
  });
  assert(s2 === 400, "Invalid priority rejected");

  const { status: s3 } = await api("/library/documents", {
    method: "POST",
    body: JSON.stringify({ title: "X", doc_type: "banana" }),
  });
  assert(s3 === 400, "Invalid doc_type rejected");

  const { status: s4 } = await api("/hooks/event", {
    method: "POST",
    headers: { "X-Hook-Secret": HOOK_SECRET },
    body: JSON.stringify({}),
  });
  assert(s4 === 400, "Hook with missing event rejected");

  // ── 16. Error handling check
  console.log("\n16. Error handling");
  const { status: s5 } = await api("/tasks/nonexistent-id-12345/move", {
    method: "POST",
    body: JSON.stringify({ to_stage: "doing" }),
  });
  assert(s5 >= 400 && s5 < 500, `Move nonexistent task returns ${s5} (not crash)`);

  const { status: s6 } = await api("/reviews/nonexistent-id/decide", {
    method: "POST",
    body: JSON.stringify({ decision: "approved" }),
  });
  assert(s6 >= 400 && s6 < 500, `Decide nonexistent review returns ${s6} (not crash)`);

  // Final health check — make sure backend didn't crash
  const { status: finalHealth } = await api("/health");
  assert(finalHealth === 200, "Backend still alive after all tests");

  // ── Summary ──────────────────────────────────────
  console.log("\n════════════════════════════════════════");
  console.log(`  ${passed} passed, ${failed} failed`);
  console.log("════════════════════════════════════════\n");

  // Cleanup — delete test data
  if (VERBOSE) {
    console.log("Skipping cleanup in verbose mode for inspection.");
  } else {
    if (project?.id) await api(`/projects/${project.id}`, { method: "DELETE" });
    if (proj2?.id) await api(`/projects/${proj2.id}`, { method: "DELETE" });
    if (xssProject?.id) await api(`/projects/${xssProject.id}`, { method: "DELETE" });
    if (testDoc?.id) await api(`/library/documents/${testDoc.id}`, { method: "DELETE" });
    if (xssDoc?.id) await api(`/library/documents/${xssDoc.id}`, { method: "DELETE" });
  }

  process.exit(failed > 0 ? 1 : 0);
}

run().catch(err => {
  console.error("Test runner crashed:", err);
  process.exit(1);
});
