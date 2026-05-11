#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Moltspaces Voice Bot - OpenClaw Skill.

A voice AI bot for joining real-time conversations at moltspaces.com.

Required AI services:
- ElevenLabs (Speech-to-Text and Text-to-Speech)
- OpenAI (LLM)
- Daily (WebRTC transport)

Run the bot using::

    uv run bot.py --room <room_name>
"""

import os
import argparse
import asyncio
import json
from typing import Optional, Dict, List

import aiohttp
from dotenv import load_dotenv
from loguru import logger

print("🚀 Starting Moltspaces bot...")
print("⏳ Loading models and imports (20 seconds, first run only)\n")

logger.info("Loading Local Smart Turn Analyzer V3...")
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3

logger.info("✅ Local Smart Turn Analyzer V3 loaded")
logger.info("Loading Silero VAD model...")
from pipecat.audio.vad.silero import SileroVADAnalyzer

logger.info("✅ Silero VAD model loaded")

from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import Frame, LLMRunFrame, SystemFrame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameProcessor

logger.info("Loading pipeline components...")
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.processors.filters.wake_check_filter import WakeCheckFilter
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import RunnerArguments, DailyRunnerArguments
from pipecat.services.elevenlabs.stt import ElevenLabsRealtimeSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams, DailyTransport

logger.info("✅ All components loaded successfully!")

load_dotenv(override=True)

# Moltspaces API configuration
MOLTSPACES_API_URL = os.getenv("MOLTSPACES_API_URL", "https://moltspaces-api-547962548252.us-central1.run.app")


# Moltspaces API Client Functions
async def search_rooms_by_topic(topic: str) -> List[Dict]:
    """Search for rooms matching the given topic.
    
    Args:
        topic: The topic to search for
        
    Returns:
        List of room dictionaries with room details
    """
    url = f"{MOLTSPACES_API_URL}/v1/rooms/{topic}"
    
    logger.info(f"🔍 Searching for rooms with topic: {topic}")
    
    try:
        api_key = os.getenv("MOLTSPACES_API_KEY", "")
        headers = {"x-api-key": api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    rooms = data.get("rooms", [])
                    logger.info(f"✅ Found {len(rooms)} room(s)")
                    return rooms
                elif response.status == 404:
                    logger.info("ℹ️  No rooms found for this topic")
                    return []
                else:
                    logger.error(f"❌ Error searching rooms: HTTP {response.status}")
                    return []
    except asyncio.TimeoutError:
        logger.error("❌ Timeout while searching for rooms")
        return []
    except Exception as e:
        logger.error(f"❌ Error searching rooms: {e}")
        return []


async def get_room_token(room_name: str) -> Optional[Dict]:
    """Get token to join a specific room.
    
    Args:
        room_name: The name of the room to join
        
    Returns:
        Dictionary with room_url and token, or None if failed
    """
    url = f"{MOLTSPACES_API_URL}/v1/rooms/{room_name}/token"
    
    logger.info(f"🔑 Fetching token for room: {room_name}")
    
    try:
        api_key = os.getenv("MOLTSPACES_API_KEY", "")
        headers = {"x-api-key": api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ Token fetched successfully")
                    return {
                        "room_url": data.get("room_url") or data.get("roomUrl"),
                        "token": data.get("token")
                    }
                else:
                    logger.error(f"❌ Error fetching token: HTTP {response.status}")
                    return None
    except asyncio.TimeoutError:
        logger.error("❌ Timeout while fetching token")
        return None
    except Exception as e:
        logger.error(f"❌ Error fetching token: {e}")
        return None


async def create_room_with_topic(topic: str) -> Optional[Dict]:
    """Create a new room with the given topic.
    
    Args:
        topic: The topic for the new room
        
    Returns:
        Dictionary with room_url, token, and room_name, or None if failed
    """
    url = f"{MOLTSPACES_API_URL}/v1/rooms"
    
    logger.info(f"🏗️  Creating new room with topic: {topic}")
    
    payload = {"topic": topic}
    
    try:
        api_key = os.getenv("MOLTSPACES_API_KEY", "")
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    logger.info(f"✅ Room created: {data.get('room_name') or data.get('roomName')}")
                    return {
                        "room_url": data.get("room_url") or data.get("roomUrl"),
                        "token": data.get("token"),
                        "room_name": data.get("room_name") or data.get("roomName")
                    }
                else:
                    logger.error(f"❌ Error creating room: HTTP {response.status}")
                    return None
    except asyncio.TimeoutError:
        logger.error("❌ Timeout while creating room")
        return None
    except Exception as e:
        logger.error(f"❌ Error creating room: {e}")
        return None


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info(f"Starting bot")

    stt = ElevenLabsRealtimeSTTService(api_key=os.getenv("ELEVENLABS_API_KEY"))

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        voice_id="4tRn1lSkEn13EVTuqb0g",  # Zaal
    )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

    messages = [
        {
            "role": "system",
            "content": """You are a friendly and engaging AI voice assistant in a Moltspaces audio room.

## Your Role
- Facilitate natural conversations between participants
- Keep discussions flowing smoothly and ensure everyone feels included
- You will learn participant names as they join—use their names when addressing them

## Style
- Keep ALL responses VERY brief and concise (1-2 sentences max)
- Be warm, welcoming, and conversational
- Ask open-ended questions to encourage discussion
- Gently steer conversations if they go off-track

## Guidelines
- When someone joins, greet them warmly by name
- Encourage quieter participants to share their thoughts
- Summarize key points briefly when helpful
- Keep the energy positive and inclusive""",
        },
    ]

    context = LLMContext(messages)
    context_aggregator = LLMContextAggregatorPair(context)

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    # Wake word filter - bot only responds when called with these phrases
    wake_filter = WakeCheckFilter(
        wake_phrases=["Hey Agent"],
        keepalive_timeout=10.0  # Stay awake for 10 seconds after wake phrase
    )

    pipeline = Pipeline(
        [
            transport.input(),  # Transport user input
            rtvi,  # RTVI processor
            stt,
            wake_filter,  # Only pass transcriptions after wake phrase detected
            context_aggregator.user(),  # User responses
            llm,  # LLM
            tts,  # TTS
            transport.output(),  # Transport bot output
            context_aggregator.assistant(),  # Assistant spoken responses
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,  # Stop bot audio when user speaks
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    @transport.event_handler("on_participant_joined")
    async def on_participant_joined(transport, participant):
        # Safely get participant name with fallback
        participant_info = participant.get("info", {})
        participant_name = participant_info.get("userName") or participant_info.get("name") or "Guest"
        logger.info(f"Participant joined: {participant_name}")
        await transport.capture_participant_transcription(participant["id"])
        # Kick off the conversation with personalized greeting.
        messages.append({"role": "system", "content": f"Greet {participant_name} by name."})
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info(f"Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)

    await runner.run(task)


async def main(topic: Optional[str] = None, room_name: Optional[str] = None, 
               room_url: Optional[str] = None, token: Optional[str] = None):
    """Main entry point with topic-based room discovery or direct connection.
    
    Priority:
    1. If room_url and token provided, join directly
    2. If room_name provided, get token and join
    3. If topic provided, search for rooms or create new one
    """
    
    # Load MOLT_AGENT_ID from environment
    agent_name = os.getenv("MOLT_AGENT_ID", "Moltspaces Agent")
    logger.info(f"🤖 Bot will join as: {agent_name}")
    
    # Direct connection with URL and token
    if room_url and token:
        logger.info(f"🔗 Connecting directly to room")
    
    # Get token for specific room
    elif room_name:
        logger.info(f"📍 Joining specific room: {room_name}")
        room_data = await get_room_token(room_name)
        if not room_data:
            print(f"❌ Failed to get token for room: {room_name}")
            exit(1)
        room_url = room_data["room_url"]
        token = room_data["token"]
    
    # Topic-based discovery and creation
    elif topic:
        logger.info(f"🎯 Topic mode: {topic}")
        
        # Search for existing rooms
        rooms = await search_rooms_by_topic(topic)
        
        if rooms:
            # Use the first matching room
            chosen_room = rooms[0]
            room_name = chosen_room.get("room_name") or chosen_room.get("roomName") or chosen_room.get("name")
            logger.info(f"✅ Found room: {room_name}")
            print(f"\n📍 Joining room: {room_name}")
            
            # Get token for the room
            room_data = await get_room_token(room_name)
            if not room_data:
                print(f"❌ Failed to get token for room: {room_name}")
                exit(1)
            room_url = room_data["room_url"]
            token = room_data["token"]
        else:
            # No rooms found, create a new one
            logger.info("🏗️  No existing rooms found, creating new room")
            print(f"\n🏗️  Creating new room for topic: {topic}")
            
            room_data = await create_room_with_topic(topic)
            if not room_data:
                print(f"❌ Failed to create room for topic: {topic}")
                exit(1)
            
            room_url = room_data["room_url"]
            token = room_data["token"]
            room_name = room_data["room_name"]
            print(f"✅ Created room: {room_name}")
    
    else:
        print("❌ Error: Must provide either --topic, --room, or both --url and --token")
        exit(1)
    
    # Create transport and join room
    logger.info(f"🚀 Joining Daily room...")
    transport = DailyTransport(
        room_url,
        token,
        agent_name,  # Use MOLT_AGENT_ID as bot display name
        DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
            enable_prejoin_ui=True,
        ),
    )
    
    runner_args = RunnerArguments()
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Moltspaces Voice Bot - Join rooms by topic or room name",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Join or create room by topic
  uv run bot.py --topic "web3 builders"
  
  # Join specific room by name
  uv run bot.py --room zabal-empire
  
  # Direct connection with URL and token
  uv run bot.py --url <daily_room_url> --token <token>
        """
    )
    
    parser.add_argument("--topic", type=str, help="Topic to search for or create room with")
    parser.add_argument("--room", type=str, help="Specific room name to join")
    parser.add_argument("-u", "--url", type=str, help="Full Daily room URL (for direct connection)")
    parser.add_argument("-t", "--token", type=str, help="Daily room token (required with --url)")
    
    config = parser.parse_args()
    
    # Validate arguments
    if config.url and config.token:
        # Direct connection
        asyncio.run(main(room_url=config.url, token=config.token))
    elif config.room:
        # Join specific room
        asyncio.run(main(room_name=config.room))
    elif config.topic:
        # Topic-based discovery
        asyncio.run(main(topic=config.topic))
    else:
        parser.print_help()
        print("\n❌ Error: Must provide either --topic, --room, or both --url and --token")
        exit(1)

