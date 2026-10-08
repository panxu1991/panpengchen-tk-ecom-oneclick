# 产品进 → 全套素材包出：编排流水线

当用户发来一个产品（产品名 / 链接 / 一句话需求），按下面流水线执行。最终交付一份落在项目目录的「素材包」：市场摸排 + 竞品分析 + 定价 + 标题/卖点/描述 + 主图/详情页 + 短视频脚本，并登记 `MANIFEST.md`。

## 触发

用户发一个产品时进入本流水线。先补齐 4 个不可省的事实，缺失则一次性问清，不逐条反复追问：

1. 目标市场与类目（默认越南，家居/厨房/收纳/清洁）。
2. 货源与成本：采购价、国内到边境仓运费、单件重量/体积、包装。
3. 履约方式（默认京东边境仓 + 平台越南尾程）。
4. 是否有实物 / 白底图（决定主图走实拍还是生成）。

补齐后按阶段顺序执行，产出未完成不跳下一阶段。

## 阶段总表（产品进 → 素材包出）

| # | 阶段 | 用哪个 skill / 工具 | 输入 | 输出 | 验证 |
|---|---|---|---|---|---|
| 0 | 产品定义 | SOP | 产品名 + 事实 | `brief.json` | 4 项事实齐全 |
| 1 | 市场摸排 | `deep-research` + headed browser | 产品关键词 | 市场报告 + 需求信号 | 每条有来源与日期 |
| 2 | 竞品分析 | `ecommerce-competitor-analysis` + headed browser | Top 竞品 listing | 竞品表（价格带/卖点/差评/图） | ≥3 个竞品、字段齐全 |
| 3 | 合规前置 | SOP `policy-snapshot.md` | 类目 | 合规检查单 | 液体/粉末/带电/锋利/食品接触/医疗/商标全查 |
| 4 | 选品打分 | `selection_score.py` | 七维评分 | 打分表 JSON | score ≥80 推进、65-79 测试 |
| 5 | 定价 | `unit_economics.py` + `表格/单位经济变量模型.xlsx` | 费率 + COGS + 重量 | 定价表 + 盈亏平衡 | 保守贡献利润 > 0 |
| 6 | 标题文案 | `listing-and-copy.md` + `product-title-optimization` | 竞品 + 关键词 | 标题 3 版 + 5 卖点 + 描述 | 文案项过 QA |
| 7 | 主图 | `ecom-image2` / `imagegen` | 底图/实拍 + 卖点 | 主图 5 张 | 每张都有产品 |
| 8 | 详情页 | `ecom-image2` / `imagegen` | 主图 + 参数 | 详情 5 张 | 统一 3:4、风格一致 |
| 9 | 短视频脚本 | `content-video.md` + `content-and-traffic.md` | 爆款拆解表 | 脚本 N 条 | 每条有钩子/结构/CTA |
| 10 | 上架 QA | `listing_qa.py` | 清单 JSON | pass/fail + 修复项 | 全项通过 |
| 11 | 打包交付 | SOP | 全部工件 | 素材包 + `MANIFEST.md` | 相对路径可解析、无编造费率 |

## 素材包目录约定

```text
products/<product-slug>/
  brief.json                 # 产品事实
  market-research.md         # 市场摸排
  competitor-analysis.md     # 竞品分析
  competitor-analysis.xlsx   # 竞品对比表（可选）
  compliance.md              # 合规检查
  selection.json             # 七维打分结果
  pricing.json               # 单位经济 + 盈亏平衡
  pricing.xlsx               # 变量模型（可选）
  listing/
    title-variants.md        # 标题 3 版
    bullets.md               # 5 个卖点
    description.md           # 短版 + 长版
  images/
    main-1..5.png            # 主图
    detail-1..5.png          # 详情页
  video/
    scripts-1..3.md          # 短视频脚本
  listing-qa.json            # 上架 QA 结果
  MANIFEST.md                # 工件清单（路径/时间/来源/状态）
```

## 三类环节，三类执行方式

- **需要网络 / browser 的环节**（1、2）：用 headed browser 在官方入口同会话核验，留下来源链接与日期；不可凭记忆编造搜索量、排名、转化数据。
- **确定性脚本环节**（4、5、10）：跑本地脚本，输入 JSON、输出 JSON，可复现、可审计。
- **生成类环节**（7、8、9）：图片用 `ecom-image2`（电商做图）或 `imagegen`，只写磁盘、不回读、不进对话；短视频脚本用文字产出，不自动生成视频。

### 图片自动化正确顺序（不用 AI 凭空画产品）
1. 从产品源链接提取全部真实主图/详情图（解析 HTML 里的 `pictureUrl`/`img` URL）。
2. 用 `rembg`（确定性抠图，不改变产品）把真实图抠成白底多体位。
3. 缺场景/实拍感图时，用「真实白底抠图当 `--img` 参考」+ AI 生成 UGC/场景图，提示词强制 `keep product appearance exactly as reference`，不能脱离参考图重画产品。
4. 越南语文字叠加后才是可上传素材；AI 生成的越南语文字必须人工核对拼写。

### 文字必须程序化叠加（AI 图上不叠字）

**教训（已实测）**：让 AI 生图模型直接在图上渲染越南语/任何非英文文字，音调符号（越南语 á/à/ả/ã/ạ 等）会被渲染错、缺声调、乱码。提示词里的文字是对的，但图上渲染必跑偏。

**正确做法**：① AI 只出「干净底图」，提示词强制 `absolutely no text, no letters`；② 用 Python PIL + 支持越南语的字体（Windows `C:/Windows/Fonts/arial.ttf` / `arialbd.ttf`）程序化叠加文字，`rounded_rectangle` 画色块 + `draw.text` 叠字，音调零错误；③ 叠字后再交付。

文字字符串先经 `underthesea.word_tokenize` 分词校验（确认是合法越南语），再交给 PIL 叠加。核心原则：**AI 出图不出字，文字永远程序化叠**。

### 国内平台反爬（已实测，写死结论）
淘宝/1688/拼多多/京东都有登录扫码+滑块/验证码，且**登录态绑定浏览器实例**：关窗口即失效，复制 profile 重启也失效，重开一次就要重新扫码。

**最终实测结论（2026-10-08）**：
1. 无人值守全自动爬不可行（扫码+滑块+会话绑定无法绕过）。
2. 可行形态是「扫码一次 + 同会话批处理」：用户登录一次并保持窗口开着，脚本在**同一不关闭的会话**里自动跑完「搜索→抓链接→进详情→评论→下载图片」全流程。
2b. 进一步实测：**复制 profile 到新浏览器实例也带不过登录态**（JD/1688/淘宝均空结果）——登录绑定浏览器指纹+会话。所以「复制 profile 采集」只对公开站点（FastMoss）有效，对登录站点无效。唯一可行是 CDP 直连用户正在运行的浏览器（需 `--remote-debugging-port`）或用户手动导出。
3. 真全自动需要基础设施：紫鸟/寻答等防关联常驻浏览器、或淘宝/1688 官方开放平台 API（需开发者账号 key）。
4. 没评论图也能闭环：源链接真实图 → `rembg` 抠白多体位（已实现）→ 越南语文案；评论实拍图是加分项。

### 仿品/IP 红线（产品如果是对标款/仿款）
若产品是「仿某品牌」（例如仿科净威云山香薰），上架前必须：①不用原品牌名/Logo/包装图；②确认云山造型是否涉设计专利；③标题卖点只讲功能不蹭品牌；④越南站商标侵权风险按类目复查。否则按侵权红线直接拦截。

## 每个环节的验证门槛

- 市场摸排：每个结论都能指向一个带日期的来源；区分 official / observed / estimated / unknown。
- 竞品分析：至少覆盖 3 个热销竞品的价格带、核心卖点、差评痛点；差评是卖点来源。
- 定价：用当前费率显式代入，不硬编码；贡献利润为负即淘汰，不「先冲量」。
- 图片：每张有产品、先纯底图再加越南语文字、`no text, no watermark`。
- 脚本：前 3 秒有钩子、有明确 CTA、一个脚本一个核心卖点。

## 交付时的固定动作

1. 生成/更新项目 `MANIFEST.md`，登记每个工件（路径、时间、来源/模型、尺寸、用途、状态、备注）。
2. 列出仍需卖家中心 / 官方确认的事项（尤其边境仓费用、清关、尾程交接、退货回程）。
3. 把不可逆动作（发布、改价、付保证金、改税号）单独标出，等授权。

## 读取用户已登录的 TikTok 卖家中心（重要）

官方核验常需读用户已登录的卖家中心（类目佣金、物流/边境仓设置、品类开放状态）。TikTok 的 `sessionid`/`SELLER_TOKEN` 是会话级，**force-kill 或自己重启浏览器会把登录态清掉**，导致跳回登录页。按下面顺序，不要自己单开新实例或反复杀用户浏览器：

1. 若用户 Edge 已用 `--remote-debugging-port=9222` 启动且已登录 → 用 Playwright `chromium.connectOverCDP('http://localhost:9222')` 直连读。
2. 否则让用户自己：关 Edge → 用带调试端口的命令重启 → 重新登录 → 保持页面开着；然后 CDP 直连。命令示例：`msedge.exe --remote-debugging-port=9222 --user-data-dir="<User Data>" https://seller.tiktokshopglobalselling.com/`。
3. 兜底：请用户截图关键页（类目佣金、物流/边境仓、品类开放状态）发回。

反模式：不要复制 profile + `launchPersistentContext` 去读 TikTok 卖家中心（cookie 加密 + 会话失效，几乎必跳登录）；不要反复 `Stop-Process -Force` 用户的浏览器。
