#!/usr/bin/env python3
"""
Artifact Manager for NotebookLM
Manages audio overviews, podcasts, and other generated artifacts.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from notebooklm_wrapper import NotebookLMWrapper, NotebookLMError
from notebook_manager import NotebookLibrary


def json_serializer(obj):
    """Custom JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def get_notebook_id(notebook_id: Optional[str] = None) -> str:
    """Get notebook ID from argument or active notebook."""
    if notebook_id:
        # Check if it's a library ID or direct NotebookLM ID
        library = NotebookLibrary()
        notebook = library.get_notebook(notebook_id)
        if notebook:
            url = notebook.get("url", "")
            if "notebook/" in url:
                parts = url.split("notebook/")
                if len(parts) > 1:
                    return parts[1].split("/")[0].split("?")[0]
        # Assume it's a direct NotebookLM ID
        return notebook_id

    # Use active notebook
    library = NotebookLibrary()
    active = library.get_active_notebook()
    if not active:
        raise ValueError("No active notebook. Run: python scripts/run.py notebook_manager.py activate --id <id>")

    url = active.get("url", "")
    if "notebook/" in url:
        parts = url.split("notebook/")
        if len(parts) > 1:
            return parts[1].split("/")[0].split("?")[0]
    raise ValueError(f"Cannot extract notebook ID from URL: {url}")


async def cmd_list(args):
    """List all artifacts in a notebook."""
    notebook_id = get_notebook_id(args.notebook_id)
    async with NotebookLMWrapper() as wrapper:
        artifacts = await wrapper.list_artifacts(notebook_id, artifact_type=args.type)

        if not artifacts:
            print("No artifacts found.")
            return

        print(f"\n🎨 Artifacts in notebook ({len(artifacts)} total):\n")
        for artifact in artifacts:
            status_icon = "✅" if artifact.get("status") == "completed" else "⏳"
            print(f"  {status_icon} [{artifact['type']}] {artifact.get('title', 'Untitled')}")
            print(f"     ID: {artifact['artifact_id']}")
            if artifact.get('created_at'):
                print(f"     Created: {artifact['created_at']}")
            if artifact.get('url'):
                print(f"     URL: {artifact['url']}")
            print()


async def cmd_get(args):
    """Get details of a specific artifact."""
    notebook_id = get_notebook_id(args.notebook_id)
    async with NotebookLMWrapper() as wrapper:
        artifact = await wrapper.get_artifact(notebook_id, args.artifact_id)
        print(json.dumps(artifact, indent=2, ensure_ascii=False, default=json_serializer))


async def cmd_delete(args):
    """Delete an artifact."""
    notebook_id = get_notebook_id(args.notebook_id)
    async with NotebookLMWrapper() as wrapper:
        await wrapper.delete_artifact(notebook_id, args.artifact_id)
        print(f"✅ Deleted artifact: {args.artifact_id}")


async def cmd_generate_audio(args):
    """Generate an audio overview (podcast) from notebook content."""
    notebook_id = get_notebook_id(args.notebook_id)

    async with NotebookLMWrapper() as wrapper:
        print("🎙️ Starting audio generation...")
        print(f"   Format: {args.format}")
        print(f"   Length: {args.length}")
        if args.instructions:
            print(f"   Instructions: {args.instructions[:50]}...")

        result = await wrapper.generate_audio(
            notebook_id,
            instructions=args.instructions or "",
            audio_format=args.format,
            audio_length=args.length,
        )

        task_id = result.get("task_id")
        print(f"   Task ID: {task_id}")

        if args.wait:
            print("\n⏳ Waiting for generation to complete...")
            final = await wrapper.wait_for_audio(
                notebook_id,
                task_id,
                timeout=args.timeout,
                poll_interval=10,
            )

            if final.get("is_complete"):
                print("✅ Audio generation complete!")
                if args.output:
                    print(f"📥 Downloading to: {args.output}")
                    path = await wrapper.download_audio(notebook_id, args.output, task_id)
                    print(f"✅ Saved to: {path}")
                elif final.get("url"):
                    print(f"🔗 URL: {final['url']}")
            elif final.get("is_failed"):
                print(f"❌ Generation failed: {final.get('error', 'Unknown error')}")
                sys.exit(1)
        else:
            print("\n💡 Use --wait to wait for completion, or check status with:")
            print(f"   python scripts/run.py artifact_manager.py status --task-id {task_id}")
            print(json.dumps(result, indent=2))


async def cmd_generate_slides(args):
    """Generate a slide deck from notebook content."""
    notebook_id = get_notebook_id(args.notebook_id)

    async with NotebookLMWrapper() as wrapper:
        print("📊 Starting slide deck generation...")
        print(f"   Format: {args.format}")
        print(f"   Length: {args.length}")
        if args.instructions:
            print(f"   Instructions: {args.instructions[:50]}...")

        result = await wrapper.generate_slide_deck(
            notebook_id,
            instructions=args.instructions or "",
            slide_format=args.format,
            slide_length=args.length,
        )

        task_id = result.get("task_id")
        print(f"   Task ID: {task_id}")

        if args.wait:
            print("\n⏳ Waiting for generation to complete...")
            final = await wrapper.wait_for_audio(
                notebook_id,
                task_id,
                timeout=args.timeout,
                poll_interval=10,
            )

            if final.get("is_complete"):
                print("✅ Slide deck generation complete!")
                if args.output:
                    print(f"📥 Downloading to: {args.output}")
                    path = await wrapper.download_slide_deck(notebook_id, args.output, task_id)
                    print(f"✅ Saved to: {path}")
                elif final.get("url"):
                    print(f"🔗 URL: {final['url']}")
            elif final.get("is_failed"):
                print(f"❌ Generation failed: {final.get('error', 'Unknown error')}")
                sys.exit(1)
        else:
            print("\n💡 Use --wait to wait for completion, or check status with:")
            print(f"   python scripts/run.py artifact_manager.py status --task-id {task_id}")
            print(json.dumps(result, indent=2))


async def cmd_generate_infographic(args):
    """Generate an infographic from notebook content."""
    notebook_id = get_notebook_id(args.notebook_id)

    async with NotebookLMWrapper() as wrapper:
        print("🖼️ Starting infographic generation...")
        print(f"   Orientation: {args.orientation}")
        print(f"   Detail Level: {args.detail_level}")
        if args.instructions:
            print(f"   Instructions: {args.instructions[:50]}...")

        result = await wrapper.generate_infographic(
            notebook_id,
            instructions=args.instructions or "",
            orientation=args.orientation,
            detail_level=args.detail_level,
        )

        task_id = result.get("task_id")
        print(f"   Task ID: {task_id}")

        if args.wait:
            print("\n⏳ Waiting for generation to complete...")
            final = await wrapper.wait_for_audio(
                notebook_id,
                task_id,
                timeout=args.timeout,
                poll_interval=10,
            )

            if final.get("is_complete"):
                print("✅ Infographic generation complete!")
                if args.output:
                    print(f"📥 Downloading to: {args.output}")
                    path = await wrapper.download_infographic(notebook_id, args.output, task_id)
                    print(f"✅ Saved to: {path}")
                elif final.get("url"):
                    print(f"🔗 URL: {final['url']}")
            elif final.get("is_failed"):
                print(f"❌ Generation failed: {final.get('error', 'Unknown error')}")
                sys.exit(1)
        else:
            print("\n💡 Use --wait to wait for completion, or check status with:")
            print(f"   python scripts/run.py artifact_manager.py status --task-id {task_id}")
            print(json.dumps(result, indent=2))


async def cmd_status(args):
    """Check status of an audio generation task."""
    notebook_id = get_notebook_id(args.notebook_id)
    async with NotebookLMWrapper() as wrapper:
        status = await wrapper.get_audio_status(notebook_id, args.task_id)

        if status.get("is_complete"):
            print("✅ Generation complete!")
            if status.get("url"):
                print(f"🔗 URL: {status['url']}")
        elif status.get("is_failed"):
            print(f"❌ Generation failed: {status.get('error', 'Unknown error')}")
        else:
            progress = status.get("progress")
            if progress:
                print(f"⏳ In progress: {progress}%")
            else:
                print(f"⏳ Status: {status.get('status', 'processing')}")

        if args.json:
            print(json.dumps(status, indent=2, ensure_ascii=False))


async def cmd_download(args):
    """Download an artifact to local file."""
    notebook_id = get_notebook_id(args.notebook_id)

    async with NotebookLMWrapper() as wrapper:
        print(f"📥 Downloading {args.type} artifact...")

        if args.artifact_id:
            path = await wrapper.download_artifact(
                notebook_id,
                args.artifact_id,
                args.output,
                artifact_type=args.type,
            )
        else:
            # Download latest audio if no artifact ID specified
            if args.type == "audio":
                path = await wrapper.download_audio(notebook_id, args.output)
            else:
                print(f"❌ Please specify --artifact-id for {args.type} downloads")
                sys.exit(1)

        print(f"✅ Downloaded to: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage NotebookLM artifacts (audio, video, slides, infographics)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    p = subparsers.add_parser("list", help="List all artifacts in a notebook")
    p.add_argument("--notebook-id", help="Notebook ID (uses active if not specified)")
    p.add_argument(
        "--type",
        choices=["audio", "video", "slide-deck", "infographic"],
        help="Filter by artifact type",
    )

    # Get command
    p = subparsers.add_parser("get", help="Get artifact details")
    p.add_argument("artifact_id", help="Artifact ID")
    p.add_argument("--notebook-id", help="Notebook ID")

    # Delete command
    p = subparsers.add_parser("delete", help="Delete an artifact")
    p.add_argument("artifact_id", help="Artifact ID")
    p.add_argument("--notebook-id", help="Notebook ID")

    # Generate audio command
    p = subparsers.add_parser("generate", help="Generate audio overview (podcast)")
    p.add_argument("--notebook-id", help="Notebook ID")
    p.add_argument("--instructions", help="Custom instructions for the podcast")
    p.add_argument(
        "--format",
        choices=["DEEP_DIVE", "BRIEF", "CRITIQUE", "DEBATE"],
        default="DEEP_DIVE",
        help="Podcast format (default: DEEP_DIVE)",
    )
    p.add_argument(
        "--length",
        choices=["SHORT", "DEFAULT", "LONG"],
        default="DEFAULT",
        help="Audio length (default: DEFAULT)",
    )
    p.add_argument("--wait", action="store_true", help="Wait for generation to complete")
    p.add_argument("--output", "-o", help="Download path (requires --wait)")
    p.add_argument("--timeout", type=int, default=600, help="Timeout in seconds (default: 600)")

    # Generate slides command
    p = subparsers.add_parser("generate-slides", help="Generate slide deck presentation")
    p.add_argument("--notebook-id", help="Notebook ID")
    p.add_argument("--instructions", help="Custom instructions for the slide deck")
    p.add_argument(
        "--format",
        choices=["DETAILED_DECK", "PRESENTER_SLIDES"],
        default="DETAILED_DECK",
        help="Slide format (default: DETAILED_DECK)",
    )
    p.add_argument(
        "--length",
        choices=["SHORT", "DEFAULT"],
        default="DEFAULT",
        help="Slide deck length (default: DEFAULT)",
    )
    p.add_argument("--wait", action="store_true", help="Wait for generation to complete")
    p.add_argument("--output", "-o", help="Download path (requires --wait)")
    p.add_argument("--timeout", type=int, default=600, help="Timeout in seconds (default: 600)")

    # Generate infographic command
    p = subparsers.add_parser("generate-infographic", help="Generate infographic")
    p.add_argument("--notebook-id", help="Notebook ID")
    p.add_argument("--instructions", help="Custom instructions for the infographic")
    p.add_argument(
        "--orientation",
        choices=["LANDSCAPE", "PORTRAIT", "SQUARE"],
        default="LANDSCAPE",
        help="Infographic orientation (default: LANDSCAPE)",
    )
    p.add_argument(
        "--detail-level",
        choices=["CONCISE", "STANDARD", "DETAILED"],
        default="STANDARD",
        help="Detail level (default: STANDARD)",
    )
    p.add_argument("--wait", action="store_true", help="Wait for generation to complete")
    p.add_argument("--output", "-o", help="Download path (requires --wait)")
    p.add_argument("--timeout", type=int, default=600, help="Timeout in seconds (default: 600)")

    # Status command
    p = subparsers.add_parser("status", help="Check audio generation status")
    p.add_argument("--task-id", required=True, help="Task ID from generate command")
    p.add_argument("--notebook-id", help="Notebook ID")
    p.add_argument("--json", action="store_true", help="Output as JSON")

    # Download command
    p = subparsers.add_parser("download", help="Download an artifact")
    p.add_argument("output", help="Output file path")
    p.add_argument("--artifact-id", help="Artifact ID (uses latest if not specified for audio)")
    p.add_argument("--notebook-id", help="Notebook ID")
    p.add_argument(
        "--type",
        choices=["audio", "video", "slide-deck", "infographic"],
        default="audio",
        help="Artifact type (default: audio)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n📚 Examples:")
        print("  # List all artifacts")
        print("  python scripts/run.py artifact_manager.py list")
        print()
        print("  # Generate a podcast and wait for completion")
        print("  python scripts/run.py artifact_manager.py generate --wait --output podcast.mp3")
        print()
        print("  # Generate with custom instructions")
        print('  python scripts/run.py artifact_manager.py generate --instructions "Focus on key findings" --format BRIEF')
        print()
        print("  # Download latest audio")
        print("  python scripts/run.py artifact_manager.py download ./my-podcast.mp3")
        return 1

    cmd_map = {
        "list": cmd_list,
        "get": cmd_get,
        "delete": cmd_delete,
        "generate": cmd_generate_audio,
        "generate-slides": cmd_generate_slides,
        "generate-infographic": cmd_generate_infographic,
        "status": cmd_status,
        "download": cmd_download,
    }

    try:
        asyncio.run(cmd_map[args.command](args))
        return 0
    except NotebookLMError as e:
        print(f"❌ [{e.code}]: {e.message}")
        if e.recovery:
            print(f"🔧 Recovery: {e.recovery}")
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
