import { query } from "@anthropic-ai/claude-agent-sdk";

/**
 * Session Management Template
 *
 * Demonstrates:
 * - Starting sessions
 * - Resuming sessions
 * - Forking sessions (alternative paths)
 * - Session lifecycle management
 */

// Start a new session
async function startSession(prompt: string): Promise<string> {
  let sessionId: string | undefined;

  const response = query({
    prompt,
    options: {
      model: "claude-sonnet-4-5"
    }
  });

  for await (const message of response) {
    if (message.type === 'system' && message.subtype === 'init') {
      sessionId = message.session_id;
      console.log(`✨ Session started: ${sessionId}`);
    } else if (message.type === 'assistant') {
      console.log('Assistant:', message.content);
    }
  }

  if (!sessionId) {
    throw new Error('Failed to start session');
  }

  return sessionId;
}

// Resume an existing session
async function resumeSession(sessionId: string, prompt: string): Promise<void> {
  const response = query({
    prompt,
    options: {
      resume: sessionId,
      model: "claude-sonnet-4-5"
    }
  });

  console.log(`\n↪️  Resuming session: ${sessionId}`);

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log('Assistant:', message.content);
    }
  }
}

// Fork a session (explore alternative path)
async function forkSession(sessionId: string, prompt: string): Promise<void> {
  const response = query({
    prompt,
    options: {
      resume: sessionId,
      forkSession: true,  // Creates new branch
      model: "claude-sonnet-4-5"
    }
  });

  console.log(`\n🔀 Forking session: ${sessionId}`);

  for await (const message of response) {
    if (message.type === 'system' && message.subtype === 'init') {
      console.log(`New session ID: ${message.session_id}`);
    } else if (message.type === 'assistant') {
      console.log('Assistant:', message.content);
    }
  }
}

// Pattern 1: Sequential Development
async function sequentialDevelopment() {
  console.log("🚀 Sequential Development Pattern\n");

  // Step 1: Initial implementation
  let session = await startSession("Create a user authentication system with JWT");

  // Step 2: Add feature
  await resumeSession(session, "Add OAuth 2.0 support (Google and GitHub)");

  // Step 3: Add tests
  await resumeSession(session, "Write comprehensive integration tests");

  // Step 4: Deploy
  await resumeSession(session, "Deploy to production with monitoring");

  console.log("\n✅ Sequential development complete");
}

// Pattern 2: Exploration & Decision
async function explorationAndDecision() {
  console.log("🔍 Exploration & Decision Pattern\n");

  // Start main conversation
  let mainSession = await startSession("Design a payment processing system");

  // Explore option A
  console.log("\n--- Option A: Stripe ---");
  await forkSession(mainSession, "Implement using Stripe API");

  // Explore option B
  console.log("\n--- Option B: PayPal ---");
  await forkSession(mainSession, "Implement using PayPal API");

  // After decision, continue with chosen approach
  console.log("\n--- Chosen: Stripe ---");
  await resumeSession(mainSession, "Implement the Stripe integration with webhooks");

  console.log("\n✅ Exploration complete");
}

// Pattern 3: Multi-User Collaboration
async function multiUserCollaboration() {
  console.log("👥 Multi-User Collaboration Pattern\n");

  // Developer A starts work
  let sessionA = await startSession("Implement user profile page with avatar, bio, and settings");

  // Developer B forks for different feature
  await forkSession(sessionA, "Add real-time notifications system with WebSockets");

  // Developer C forks for another feature
  await forkSession(sessionA, "Implement search functionality with filters and sorting");

  // All developers can work independently without interfering
  console.log("\n✅ Multi-user collaboration setup complete");
}

// Run examples
async function main() {
  try {
    // Choose one pattern to run
    await sequentialDevelopment();
    // await explorationAndDecision();
    // await multiUserCollaboration();
  } catch (error) {
    console.error('Error:', error);
  }
}

main();
