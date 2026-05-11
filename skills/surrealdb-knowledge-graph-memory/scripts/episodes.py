#!/usr/bin/env python3
"""
Episodic Memory - Task Histories and Learning from Experience

This module manages episodes (complete task narratives) in the knowledge graph,
enabling the agent to learn from past experiences and recall relevant strategies.

Usage:
    from episodes import EpisodicMemory
    
    em = EpisodicMemory()
    episode_id = em.store_episode(episode_data)
    similar = em.find_similar_episodes("Deploy marketing pipeline")
    em.update_fact_outcomes(episode_id, outcome="success")
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# Configuration
SURREAL_CONFIG = {
    "connection": os.environ.get("SURREAL_URL", "http://localhost:8000"),
    "namespace": "openclaw",
    "database": "memory",
    "user": os.environ.get("SURREAL_USER", "root"),
    "password": os.environ.get("SURREAL_PASS", "root"),
}

SYNC_WRITE_THRESHOLD = 0.7  # Facts above this importance get written immediately

try:
    from surrealdb import Surreal
    import openai
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


def get_db():
    """Get database connection."""
    if not DEPS_AVAILABLE:
        return None
    db = Surreal(SURREAL_CONFIG["connection"])
    db.signin({"username": SURREAL_CONFIG["user"], "password": SURREAL_CONFIG["password"]})
    db.use(SURREAL_CONFIG["namespace"], SURREAL_CONFIG["database"])
    return db


def close_db(db):
    """Safely close database connection."""
    if db:
        try:
            db.close()
        except (NotImplementedError, AttributeError):
            pass


def get_embedding(text: str) -> list:
    """Generate embedding for text."""
    if not DEPS_AVAILABLE:
        return []
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return []
    client = openai.OpenAI(api_key=api_key)
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding


class EpisodicMemory:
    """
    Manages episodic memory - complete task narratives with semantic search.
    
    Episodes capture:
    - What task was attempted
    - What decisions were made
    - What problems were encountered
    - What solutions worked
    - What was learned
    """
    
    def __init__(self, agent_id: str = "main"):
        self.agent_id = agent_id
    
    def store_episode(self, episode_data: Dict[str, Any]) -> Optional[str]:
        """
        Store a completed episode in the knowledge graph.
        
        Args:
            episode_data: Dict from WorkingMemory.complete_task()
        
        Returns:
            Episode ID if successful
        """
        if not DEPS_AVAILABLE:
            return None
        
        try:
            db = get_db()
            
            # Create embedding from goal + key learnings
            embed_text = f"{episode_data.get('goal', '')} {' '.join(episode_data.get('key_learnings', []))}"
            embedding = get_embedding(embed_text) if embed_text.strip() else None
            
            # Use SurrealQL query to handle datetime properly
            # SurrealDB requires datetime values via time::now() or time::parse()
            result = db.query("""
                CREATE episode SET
                    task = $task,
                    goal = $goal,
                    started_at = time::now(),
                    completed_at = time::now(),
                    outcome = $outcome,
                    duration_hours = $duration_hours,
                    steps_taken = $steps_taken,
                    decisions = $decisions,
                    problems = $problems,
                    solutions = $solutions,
                    key_learnings = $key_learnings,
                    facts_used = $facts_used,
                    facts_created = $facts_created,
                    embedding = $embedding,
                    session_key = $session_key,
                    agent_id = $agent_id,
                    metadata = $metadata
            """, {
                "task": episode_data.get("task", ""),
                "goal": episode_data.get("goal", ""),
                "outcome": episode_data.get("outcome", "unknown"),
                "duration_hours": episode_data.get("duration_hours"),
                "steps_taken": episode_data.get("steps_taken", 0),
                "decisions": episode_data.get("decisions", []),
                "problems": [p if isinstance(p, str) else str(p) for p in episode_data.get("problems", [])],
                "solutions": [s if isinstance(s, str) else str(s) for s in episode_data.get("solutions", [])],
                "key_learnings": episode_data.get("key_learnings", []),
                "facts_used": episode_data.get("facts_used", []),
                "facts_created": episode_data.get("facts_created", []),
                "embedding": embedding,
                "session_key": episode_data.get("session_key"),
                "agent_id": episode_data.get("agent_id", self.agent_id),
                "metadata": {"final_confidence": episode_data.get("final_confidence", 0.5)}
            })
            
            # Extract episode ID from result
            episode_id = None
            if isinstance(result, list) and result:
                first = result[0]
                if isinstance(first, dict):
                    episode_id = str(first.get("id", ""))
            elif isinstance(result, dict):
                episode_id = str(result.get("id", ""))
            
            # Update fact outcomes based on episode result
            if episode_id and episode_data.get("outcome") in ["success", "failure"]:
                self._update_fact_outcomes(
                    db,
                    episode_data.get("facts_used", []),
                    episode_data.get("outcome")
                )
            
            close_db(db)
            return episode_id
            
        except Exception as e:
            print(f"Error storing episode: {e}")
            return None
    
    def _update_fact_outcomes(self, db, fact_ids: List[str], outcome: str):
        """Update outcome counters on facts used in this episode."""
        for fact_id in fact_ids:
            try:
                if outcome == "success":
                    db.query(f"""
                        UPDATE {fact_id} SET 
                            success_count = success_count + 1,
                            last_outcome = 'success'
                    """)
                elif outcome == "failure":
                    db.query(f"""
                        UPDATE {fact_id} SET 
                            failure_count = failure_count + 1,
                            last_outcome = 'failure'
                    """)
            except Exception as e:
                print(f"Warning: Could not update fact {fact_id}: {e}")
    
    def find_similar_episodes(
        self,
        query: str,
        limit: int = 5,
        outcome_filter: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find episodes similar to a query/goal.
        
        Args:
            query: Search query (usually the current task goal)
            limit: Max results
            outcome_filter: Filter by outcome (success, failure, or None for all)
        
        Returns:
            List of similar episodes with relevance scores
        """
        if not DEPS_AVAILABLE:
            return []
        
        try:
            db = get_db()
            embedding = get_embedding(query)
            
            if not embedding:
                # Fallback to text search
                results = db.query("""
                    SELECT * FROM episode
                    WHERE goal CONTAINS $query OR task CONTAINS $query
                    ORDER BY completed_at DESC
                    LIMIT $limit
                """, {"query": query, "limit": limit})
            else:
                # Semantic search
                where_clause = "embedding IS NOT NONE AND agent_id = $agent_id"
                if outcome_filter:
                    where_clause += f" AND outcome = '{outcome_filter}'"
                
                results = db.query(f"""
                    SELECT *,
                        vector::similarity::cosine(embedding, $embedding) AS similarity
                    FROM episode
                    WHERE {where_clause}
                    ORDER BY similarity DESC
                    LIMIT $limit
                """, {"embedding": embedding, "agent_id": self.agent_id, "limit": limit})
            
            close_db(db)
            
            episodes = results if isinstance(results, list) else []
            return [
                {
                    "id": str(ep.get("id", "")),
                    "goal": ep.get("goal", ""),
                    "outcome": ep.get("outcome", ""),
                    "duration_hours": ep.get("duration_hours"),
                    "decisions": ep.get("decisions", []),
                    "problems": ep.get("problems", []),
                    "solutions": ep.get("solutions", []),
                    "key_learnings": ep.get("key_learnings", []),
                    "similarity": ep.get("similarity", 0),
                    "completed_at": str(ep.get("completed_at", ""))
                }
                for ep in episodes
            ]
            
        except Exception as e:
            print(f"Error finding episodes: {e}")
            return []
    
    def get_episode(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific episode by ID."""
        if not DEPS_AVAILABLE:
            return None
        
        try:
            db = get_db()
            result = db.select(episode_id)
            close_db(db)
            return result if isinstance(result, dict) else result[0] if result else None
        except Exception as e:
            print(f"Error getting episode: {e}")
            return None
    
    def get_learnings_for_task(self, task_goal: str, limit: int = 10) -> List[str]:
        """
        Get relevant learnings from past similar tasks.
        
        Returns a flat list of key learnings from similar episodes.
        """
        similar = self.find_similar_episodes(task_goal, limit=5, outcome_filter=None)
        
        learnings = []
        for ep in similar:
            # Prioritize successful episode learnings
            if ep.get("outcome") == "success":
                learnings.extend(ep.get("key_learnings", []))
            # Also include failure warnings
            elif ep.get("outcome") == "failure":
                for problem in ep.get("problems", []):
                    if isinstance(problem, dict):
                        learnings.append(f"⚠️ Past failure: {problem.get('problem', '')}")
                    else:
                        learnings.append(f"⚠️ Past failure: {problem}")
        
        return learnings[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get episodic memory statistics."""
        if not DEPS_AVAILABLE:
            return {"error": "Dependencies not available"}
        
        try:
            db = get_db()
            
            total = db.query("SELECT count() FROM episode GROUP ALL")
            successes = db.query("SELECT count() FROM episode WHERE outcome = 'success' GROUP ALL")
            failures = db.query("SELECT count() FROM episode WHERE outcome = 'failure' GROUP ALL")
            avg_duration = db.query("SELECT math::mean(duration_hours) AS avg FROM episode WHERE duration_hours IS NOT NONE GROUP ALL")
            
            close_db(db)
            
            return {
                "total_episodes": total[0].get("count", 0) if total else 0,
                "successes": successes[0].get("count", 0) if successes else 0,
                "failures": failures[0].get("count", 0) if failures else 0,
                "avg_duration_hours": avg_duration[0].get("avg", 0) if avg_duration else 0,
            }
            
        except Exception as e:
            return {"error": str(e)}


class SyncFactWriter:
    """
    Handles synchronous fact writes for high-importance discoveries.
    
    Facts above the importance threshold get written immediately;
    lower-importance facts queue for batch extraction.
    """
    
    def __init__(self, agent_id: str = "main", threshold: float = SYNC_WRITE_THRESHOLD):
        self.agent_id = agent_id
        self.threshold = threshold
    
    def store_fact_sync(
        self,
        content: str,
        importance: float = 0.5,
        source: str = "inferred",
        confidence: float = None,
        tags: List[str] = None,
        scope: str = "agent",
        client_id: str = None
    ) -> Optional[str]:
        """
        Store a fact, synchronously if importance is high enough.
        
        Args:
            content: The fact content
            importance: How important this fact is (0-1)
            source: explicit, inferred, etc.
            confidence: Fact confidence (defaults based on source)
            tags: Categorization tags
            scope: global, client, or agent
            client_id: For client-scoped facts
        
        Returns:
            Fact ID if stored synchronously, None if queued for batch
        """
        if importance < self.threshold:
            # Queue for batch extraction (return None, caller should log to daily file)
            return None
        
        if not DEPS_AVAILABLE:
            return None
        
        # Set default confidence based on source
        if confidence is None:
            confidence = 0.9 if source == "explicit" else 0.7
        
        try:
            db = get_db()
            embedding = get_embedding(content)
            
            result = db.create("fact", {
                "content": content,
                "embedding": embedding,
                "source": source,
                "confidence": confidence,
                "tags": tags or [],
                "scope": scope,
                "client_id": client_id,
                "agent_id": self.agent_id,
                "success_count": 0,
                "failure_count": 0
            })
            
            fact_id = result[0]["id"] if isinstance(result, list) else result.get("id")
            close_db(db)
            
            return str(fact_id)
            
        except Exception as e:
            print(f"Error storing fact: {e}")
            return None


# ============================================
# CLI Interface
# ============================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Episodic Memory CLI")
    parser.add_argument("action", choices=["find", "get", "stats", "learnings"])
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--id", help="Episode ID")
    parser.add_argument("--outcome", help="Filter by outcome")
    parser.add_argument("--limit", type=int, default=5)
    
    args = parser.parse_args()
    em = EpisodicMemory()
    
    if args.action == "find":
        if not args.query:
            print("Error: --query required")
            return
        episodes = em.find_similar_episodes(args.query, args.limit, args.outcome)
        for ep in episodes:
            sim = ep.get("similarity", 0)
            print(f"[{sim:.2f}] {ep['outcome']:8} | {ep['goal'][:60]}")
            if ep.get("key_learnings"):
                for learning in ep["key_learnings"][:2]:
                    print(f"    → {learning[:70]}")
    
    elif args.action == "get":
        if not args.id:
            print("Error: --id required")
            return
        ep = em.get_episode(args.id)
        if ep:
            print(json.dumps(ep, indent=2, default=str))
        else:
            print("Episode not found")
    
    elif args.action == "stats":
        stats = em.get_stats()
        print(f"Total episodes: {stats.get('total_episodes', 0)}")
        print(f"Successes: {stats.get('successes', 0)}")
        print(f"Failures: {stats.get('failures', 0)}")
        print(f"Avg duration: {stats.get('avg_duration_hours', 0):.1f}h")
    
    elif args.action == "learnings":
        if not args.query:
            print("Error: --query required")
            return
        learnings = em.get_learnings_for_task(args.query, args.limit)
        for learning in learnings:
            print(f"• {learning}")


if __name__ == "__main__":
    main()
