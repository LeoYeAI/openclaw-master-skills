"""不调用蝉镜 API：校验 run_render 纯函数；ID 解析见 test_id_resolver。"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import run_render as rr  # noqa: E402
import test_id_resolver as tid  # noqa: E402


class TestRunRenderStub(unittest.TestCase):
    def test_norm_text(self):
        self.assertEqual(rr.norm_text("a  b\nc\r"), "abc")

    def test_group_scene_batches_respects_limit(self):
        scenes = [
            {"scene_id": i, "voiceover": "x" * 2000, "use_avatar": True}
            for i in range(1, 4)
        ]
        batches = rr.group_scene_batches(scenes)
        self.assertGreaterEqual(len(batches), 2)
        for b in batches:
            self.assertLessEqual(
                sum(len(s["voiceover"]) for s in b), rr.TTS_BATCH_MAX
            )

    def test_compute_scene_times_low_prop_when_subs_shorter(self):
        scenes = [
            {"scene_id": 1, "voiceover": "AAAA", "use_avatar": True},
            {"scene_id": 2, "voiceover": "BBBB", "use_avatar": False},
        ]
        subtitles = [
            {"start_time": 0.0, "end_time": 1.0, "subtitle": "AA"},
            {"start_time": 1.0, "end_time": 2.0, "subtitle": "BB"},
        ]
        times, q = rr.compute_scene_times(
            scenes, "AAAABBBB", subtitles, 10.0
        )
        self.assertEqual(q, "low_prop")
        self.assertEqual(len(times), 2)
        self.assertAlmostEqual(times[0][1], times[1][0], places=5)

    def test_compute_scene_times_high_when_subs_match(self):
        scenes = [
            {"scene_id": 1, "voiceover": "你好", "use_avatar": True},
            {"scene_id": 2, "voiceover": "世界", "use_avatar": False},
        ]
        subtitles = [
            {"start_time": 0.0, "end_time": 1.0, "subtitle": "你好"},
            {"start_time": 1.0, "end_time": 2.0, "subtitle": "世界"},
        ]
        times, q = rr.compute_scene_times(
            scenes, "你好世界", subtitles, 2.0
        )
        self.assertEqual(q, "high")
        self.assertAlmostEqual(times[0][1], 1.05, places=2)
        self.assertLess(times[1][0], times[1][1])

    def test_normalize_chan_skills_repo_root_accepts_skills_subdir(self):
        repo = rr.repo_root_from_script()
        sub = repo / "skills"
        self.assertEqual(rr.normalize_chan_skills_repo_root(repo), repo)
        self.assertEqual(rr.normalize_chan_skills_repo_root(sub), repo)

    def test_default_ref_shape(self):
        r = rr.default_ref()
        self.assertEqual(r["width"], 1080)
        self.assertEqual(r["height"], 1920)

    def test_display_size_from_stream_rotate_90(self):
        w, h = rr.display_size_from_stream(
            {"width": 1920, "height": 1080, "tags": {"rotate": "90"}}
        )
        self.assertEqual((w, h), (1080, 1920))

    def test_ref_to_ai_submit_params_portrait_1080(self):
        ar, cl = rr.ref_to_ai_submit_params(
            {"width": 1080, "height": 1920, "fps": 25.0, "pix_fmt": "yuv420p", "a_rate": 48000}
        )
        self.assertEqual(ar, "9:16")
        self.assertEqual(cl, 1080)

    def test_ref_to_ai_submit_params_portrait_720(self):
        ar, cl = rr.ref_to_ai_submit_params(
            {"width": 720, "height": 1280, "fps": 30.0, "pix_fmt": "yuv420p", "a_rate": 48000}
        )
        self.assertEqual(ar, "9:16")
        self.assertEqual(cl, 720)

    def test_build_ai_segment_prompt_varies_after_first(self):
        base = "Ancient camp, maps, Han dynasty, vertical 9:16."
        self.assertEqual(rr.build_ai_segment_prompt(base, 0, 1), base)
        p0 = rr.build_ai_segment_prompt(base, 0, 2)
        p1 = rr.build_ai_segment_prompt(base, 1, 2)
        self.assertIn("Ancient camp", p0)
        self.assertIn("Ancient camp", p1)
        self.assertIn("[SHOT 1/2", p0)
        self.assertIn("OPENING]", p0)
        self.assertIn("[SHOT 2/2", p1)
        self.assertIn("PRIMARY ACTION]", p1)
        self.assertNotEqual(p0, p1)
        p3 = rr.build_ai_segment_prompt(base, 3, 5)
        self.assertIn("CONTRAST OUT]", p3)

    def test_example_workflow_accepts_resolved_test_ids(self):
        """
        使用 test_id_resolver 的配置/内嵌默认/缓存逻辑填充 ID，校验 JSON 结构可被 run_render 解析。
        """
        ex = ROOT / "examples" / "workflow-input.example.json"
        if not ex.is_file():
            self.skipTest("缺少 examples/workflow-input.example.json")

        payload = json.loads(ex.read_text(encoding="utf-8"))
        try:
            ids = tid.resolve_render_test_ids(force_refresh=False)
        except Exception as e:
            self.skipTest(
                "无法自动解析测试 ID（可复制 tests/chanjing_test_defaults.example.json 为 "
                f"chanjing_test_defaults.json 填写 ID，或配置 ~/.chanjing/credentials.json）：{e}"
            )
        payload["audio_man"] = ids["audio_man"]
        payload["person_id"] = ids["person_id"]
        payload["figure_type"] = ids.get("figure_type") or tid.DEFAULT_TEST_FIGURE_TYPE

        self.assertTrue(payload["audio_man"])
        self.assertTrue(payload["person_id"])
        self.assertTrue(payload["full_script"])
        joined = "".join(s["voiceover"] for s in sorted(payload["scenes"], key=lambda x: int(x["scene_id"])))
        self.assertEqual(rr.norm_text(joined), rr.norm_text(payload["full_script"]))


if __name__ == "__main__":
    unittest.main()
