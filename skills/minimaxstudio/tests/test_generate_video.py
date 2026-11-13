"""Offline regression tests for H3 and legacy video generation."""

import argparse
import contextlib
import importlib.util
import io
import pathlib
import tempfile
import unittest
from unittest.mock import Mock, patch

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts/video/generate_video.py"
spec = importlib.util.spec_from_file_location("generate_video", SCRIPT)
video = importlib.util.module_from_spec(spec)
spec.loader.exec_module(video)


def args(**changes):
    values = dict(
        mode="t2v", model="MiniMax-H3", prompt="A bird flying over the sea",
        duration=10, resolution=None, prompt_optimizer=None, fast_pretreatment=None,
        callback_url=None, aigc_watermark=None, first_frame=None, last_frame=None,
        subject_image=None, reference_video=None, reference_audio=None,
        region="global_en", ratio=None,
    )
    values.update(changes)
    return argparse.Namespace(**values)


def response(data=None, content=b"video"):
    result = Mock()
    result.json.return_value = data
    result.content = content
    return result


class VideoTests(unittest.TestCase):
    def setUp(self):
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def test_h3_payload_and_duration_boundaries(self):
        for duration in (4, 10, 15):
            with self.subTest(duration=duration):
                payload = video.build_payload(args(duration=duration))
                self.assertEqual(payload, {
                    "model": "MiniMax-H3", "duration": duration, "resolution": "2K",
                    "ratio": "16:9", "content": [
                        {"type": "text", "text": "A bird flying over the sea"}],
                })

    def test_invalid_h3_parameters(self):
        invalid = [dict(duration=value) for value in (3, 16, 4.5, True, None)]
        invalid += [dict(prompt=value) for value in (None, " ", "x" * 7001)]
        invalid += [dict(resolution="768P"), dict(ratio="adaptive"),
                    dict(prompt_optimizer=False), dict(fast_pretreatment=True),
                    dict(aigc_watermark=0), dict(first_frame="https://example.com/a.png")]
        for values in invalid:
            with self.subTest(values=list(values)):
                with self.assertRaises(ValueError):
                    video.build_payload(args(**values))

    def test_frame_content_and_local_image(self):
        with tempfile.TemporaryDirectory() as directory:
            image = pathlib.Path(directory) / "frame.png"
            image.write_bytes(b"image")
            payload = video.build_payload(args(
                mode="sef", first_frame=str(image), last_frame="https://example.com/end.png"))
        self.assertEqual(payload["ratio"], "adaptive")
        self.assertEqual(payload["content"][1], {
            "type": "image_url", "image_url": {"url": "data:image/png;base64,aW1hZ2U="},
            "role": "first_frame",
        })
        self.assertEqual(payload["content"][2]["role"], "last_frame")
        self.assertNotIn("first_frame_image", payload)

    def test_reference_content(self):
        payload = video.build_payload(args(
            mode="ref", subject_image="https://example.com/ref.png",
            reference_video="https://example.com/ref.mp4",
            reference_audio="https://example.com/ref.wav"))
        self.assertEqual([item.get("role") for item in payload["content"]],
                         [None, "reference_image", "reference_video", "reference_audio"])
        self.assertEqual(payload["content"][2]["video_url"]["url"],
                         "https://example.com/ref.mp4")

    def test_invalid_content_combinations(self):
        invalid = [
            dict(mode="ref", reference_audio="https://example.com/ref.wav"),
            dict(mode="i2v"),
            dict(mode="ref", first_frame="https://example.com/a.png",
                 subject_image="https://example.com/b.png"),
            dict(mode="i2v", first_frame="https://example.com/a.png",
                 last_frame="https://example.com/b.png"),
            dict(mode="ref", reference_video="local.mp4"),
        ]
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(ValueError):
                video.build_payload(args(**values))

    def test_watermark_and_callback(self):
        payload = video.build_payload(args(region="cn_zh", aigc_watermark=1,
                                           callback_url="https://example.com/callback"))
        self.assertIs(payload["aigc_watermark"], True)
        self.assertEqual(payload["callback_url"], "https://example.com/callback")

    def test_create_endpoints_for_each_region_and_version(self):
        for region, host in (("global_en", "api.minimax.io"), ("cn_zh", "api.minimaxi.com")):
            for model, version in (("MiniMax-H3", "v2"), ("MiniMax-Hailuo-2.3", "v1")):
                with self.subTest(region=region, version=version), patch.object(
                        video.requests, "post", return_value=response({"task_id": "123"})) as post:
                    self.assertEqual(video.create_task({"model": model}, {}, region), "123")
                    self.assertEqual(post.call_args.args[0], f"https://{host}/{version}/video_generation")

    def test_v2_poll_and_direct_download(self):
        url = "https://example.com/output.mp4"
        replies = [response({"task": {"status": status}}) for status in ("queued", "running")]
        replies += [response({"task": {"status": "succeeded", "content": {"url": url}}}), response()]
        with patch.object(video.requests, "get", side_effect=replies) as get, \
                patch.object(video.time, "sleep") as sleep, tempfile.TemporaryDirectory() as directory:
            status, result = video.poll_task("123", {"Authorization": "Bearer dummy"}, "global_en", "v2")
            self.assertEqual((status, result), ("succeeded", url))
            self.assertEqual(get.call_args.args[0], "https://api.minimax.io/v2/query/video_generation/123")
            self.assertIsNone(get.call_args.kwargs["params"])
            output = pathlib.Path(directory) / "out.mp4"
            video.download_video(result, output, {"Authorization": "Bearer dummy"}, "global_en", "v2")
            get.assert_called_with(url, timeout=180)
            self.assertEqual(output.read_bytes(), b"video")
            self.assertEqual(sleep.call_count, 2)

    def test_v2_terminal_errors(self):
        for status in ("failed", "cancelled"):
            with self.subTest(status=status), patch.object(video.requests, "get", return_value=response(
                    {"task": {"status": status, "error": {"message": "generation rejected"}}})):
                with self.assertRaisesRegex(RuntimeError, status):
                    video.poll_task("123", {}, api_version="v2")
        with patch.object(video.requests, "get", return_value=response({"task": {"status": "succeeded"}})):
            with self.assertRaisesRegex(RuntimeError, "task.content.url"):
                video.poll_task("123", {}, api_version="v2")

    def test_legacy_payload_and_round_trip(self):
        payload = video.build_payload(args(model="MiniMax-Hailuo-2.3", mode="i2v",
                                           first_frame="https://example.com/frame.png"))
        self.assertEqual(payload["first_frame_image"], "https://example.com/frame.png")
        self.assertEqual(payload["resolution"], "768P")
        self.assertNotIn("content", payload)
        replies = [response({"status": "Success", "file_id": "file123"}),
                   response({"file": {"download_url": "https://example.com/legacy.mp4"}}), response()]
        with patch.object(video.requests, "get", side_effect=replies) as get, tempfile.TemporaryDirectory() as directory:
            self.assertEqual(video.poll_task("123", {}), ("Success", "file123"))
            self.assertEqual(get.call_args.args[0], "https://api.minimaxi.com/v1/query/video_generation")
            self.assertEqual(get.call_args.kwargs["params"], {"task_id": "123"})
            video.download_video("file123", pathlib.Path(directory) / "out.mp4", {})
            self.assertEqual(get.call_args_list[1].args[0], "https://api.minimaxi.com/v1/files/retrieve")

    def test_shared_caller_retains_legacy_defaults(self):
        namespace = args(model=None)
        for name in ("ratio", "reference_video", "reference_audio", "region"):
            delattr(namespace, name)
        payload = video.build_payload(namespace)
        self.assertEqual(payload["model"], "MiniMax-Hailuo-2.3")
        self.assertIn("prompt", payload)
        self.assertNotIn("content", payload)

    def test_cli_propagates_h3_region_and_version(self):
        argv = ["generate_video.py", "--mode", "t2v", "--prompt", "A bird", "--region", "global_en",
                "--output", "out.mp4"]
        with patch.object(video.sys, "argv", argv), patch.dict(video.os.environ, {"MINIMAX_API_KEY": "dummy"}), \
                patch.object(video, "create_task", return_value="123") as create, \
                patch.object(video, "poll_task", return_value=("succeeded", "https://example.com/out.mp4")) as poll, \
                patch.object(video, "download_video") as download:
            self.assertEqual(video.main(), 0)
            self.assertEqual(create.call_args.args[0]["model"], "MiniMax-H3")
            self.assertEqual(create.call_args.args[0]["resolution"], "2K")
            self.assertEqual(poll.call_args.args[2:], ("global_en", "v2"))
            self.assertEqual(download.call_args.args[3:], ("global_en", "v2"))


if __name__ == "__main__":
    unittest.main()
