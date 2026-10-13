# 媒体核验，2026-10-13

运行 `python _build/build_media.py` 成功，PowerPoint 独立 COM 实例结束；两段视频及所有5张关键帧 PNG 落在 `media/`。静态帧逐张目视检查：中文可读，无裁切、错位或空白。动态内容是5帧定时切换，未声称原始UI录屏。

| 视频 | PPTX/PNG 帧 | MP4 文件大小 | 容器核验 |
|---|---:|---:|---|
| `anthropic_cycle.mp4` | 2帧 | 949,548 bytes | `avc1` 视频轨；`mvhd` 时间尺度25,000、时长250,000，10.0秒 |
| `smoke_log_replay.mp4` | 3帧 | 1,460,490 bytes | `avc1` 视频轨；`mvhd` 时间尺度25,000、时长450,000，18.0秒 |

来源核对：smoke 回放的事件与 `practice/runs/smoke/actions.jsonl` 和 `output.json` 对照；首四项动作是事后补记，时间不精确，画面已注明重排和非真实速度。Anthropic 视频按公开 AAR §2–3 方法示意重绘，已标注不是公司运行影像。PowerPoint 输出的 MP4 没有音轨，符合静音要求。尚未用独立解码器逐帧检查视频压缩画面；用 PowerPoint 导出 PNG 作为静态替代并完成目视检查。

实验声明：`practice/runs/demo/freeze.json` 明示本轮 demo 为16题单批次、各变体独立上下文，偏离逐题独立协议；共享目录没有OS隔离，答案已对制作代理可见。此媒体只回放独立 smoke，不展示或暗示任何 demo 提升。
