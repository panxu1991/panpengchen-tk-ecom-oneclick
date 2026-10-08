# 短视频成片环节（脚本 → 素材 → 一键成片）

> **结论**：本 SKILL 原有「脚本」环节（15 AI + 5 真人），缺「脚本 → 成片」的后半段。已找到成熟免费工具：**`xianyu110/ecommerce-video-skills`（MIT，无需 API Key，本地 ffmpeg + edge-tts）**，13 个技能，一张商品图 → 带配音/字幕/BGM 的 9:16 成片。本文件蒸馏其流水线并给出接入方式。

## 一、工具结论（满足全部要求）

| 你的要求 | 对应能力 | 是否满足 |
|---|---|---|
| 免费 | MIT，本地 Python + ffmpeg + edge-tts，无 API Key | ✅ |
| 根据脚本生成素材 | selling-point-storyboard（分镜）、multi-model-shot-prompts（多模型镜头提示词）、image-to-video-shots（图生视频） | ✅ |
| 一键成片 | ffmpeg-auto-assemble（`assemble.py` 一条命令 → 9:16 MP4） | ✅ |
| 翻译越南语/多国语言 | multilingual-dubbing（`vi-VN-HoaiMyNeural` 越南音色；印尼/泰/越/马来/菲律宾/日韩/西语） | ✅ |
| 自我检索 | viral-remake（丢链接/转写 → 拆 8 维 + 5-beat 结构 → 复刻分镜） | ✅ |
| 自动修正 | 广告法绝对化用语检查、商品一致性锁（先锁形状/颜色/Logo）、只写测过的数据 | ✅ |

## 二、成片流水线（脚本 → 成片）

```
1. 脚本（本 SKILL 已有：15 AI + 5 真人）
   ↓
2. selling-point-storyboard：脚本 → storyboard.json（分镜：钩子→问题→方案→证明→CTA）
   ↓
3. image-to-video-shots / multi-model-shot-prompts：分镜 → 每个镜头的画面素材（图生视频为可选项，本地 Ken Burns 兜底）
   ↓
4. ai-voiceover-edge-tts：逐句配音（edge-tts 免费，越南 vi-VN-HoaiMyNeural）
   ↓
5. multilingual-dubbing：本地化改写口播（非直译）+ 多语言渲染
   ↓
6. ffmpeg-auto-assemble：assemble.py 本地渲染 → 9:16 MP4（配音+字幕花字+转场+BGM 自动闪避+响度标准化）
   ↓
7. cover-title-ab / platform-spec-export：封面 AB + 平台规格导出（抖音/TikTok Shop/视频号/小红书/淘宝/Amazon）
```

## 三、接入方式（安装）

```bash
# 方式一：一行安装（skills CLI）
npx skills add xianyu110/ecommerce-video-skills

# 方式二：手动（Codex）
git clone https://github.com/xianyu110/ecommerce-video-skills.git
cp -r ecommerce-video-skills/skills/* ~/.codex/skills/
pip install pillow numpy edge-tts      # 另需 ffmpeg（含 libass）+ CJK 字体
```

本机已有副本：`D:\越南TK电商\交付-20261008\_video-review\ecommerce-video-skills-main\`。

## 四、与本 SKILL 的衔接

- 本 SKILL 步骤 7 产出**脚本**（15 AI + 5 真人）→ 后续直接用 `selling-point-storyboard` 转成 `storyboard.json` → `assemble.py` 成片。
- 越南语版本：`assemble.py storyboard.json --lang vi --voice vi-VN-HoaiMyNeural -o out/video-vi.mp4`（具体 `--lang` 代码以仓库为准）。
- **图生视频是可选增强**（Seedance/可灵/Veo/Runway/海螺/万相 多模型提示词），没有时用本地 Ken Burns 兜底，不编造模型价格。

## 五、铁律衔接

- 商品一致性锁：图生视频提示词第一步锁形状/颜色/Logo，杜绝「视频很酷但商品变了」——与本 SKILL「AI 不凭空画产品」同源。
- 越南语口播用 edge-tts 合成音（不是 AI 图上叠字），音调由 TTS 引擎保证；字幕/花字仍走程序化（assemble.py 的 make_subs.py）。
- 只写测过的数据：广告法绝对化用语检查，避免「吸潮除霉」类无依据宣称。
