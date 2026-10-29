<a id="english"></a>

<div align="center">

# ✨ Copilot Cowork Skills

**Turn everyday research, organization, and preparation into reusable Cowork skills.**

Created by **Geek Fujiwara** · Released under the **MIT License**

[![License: MIT](https://img.shields.io/badge/License-MIT-2563EB.svg)](LICENSE)

<a href="#japanese"><kbd>日本語は下 ↓</kbd></a>

[Concept](#concept) · [Design principles](#design-principles-for-shared-organizational-knowledge) · [Categories](#categories) · [Skills](#skills) · [Installation](#installation) · [Usage](#usage)

</div>

---

## Concept

**Make ways of working reusable and open to improvement, rather than leaving them as knowledge held by a few individuals.**

This repository is a public collection of Copilot Cowork skills, with workflows primarily written in Japanese. It shares business workflows across calendars, email, Teams, SharePoint, OneDrive, Office files, and the public web without embedding personal information or organization-specific names.

Skills do not freeze a finished answer. They are reusable design assets that check the policies, past examples, required templates, conversations, and documents the user can already access at runtime, then adapt research, reasoning, and deliverables to that organization. The goal is to let anyone use the published skills and contribute improvements back to their organization or the community.

## Design principles for shared organizational knowledge

1. **Generalize** — Obtain names, email addresses, customer names, tenant URLs, and IDs from user input or runtime context instead of hardcoding them.
2. **Check organizational facts first** — Consult available internal policies, successful examples, required templates, budgets, and past decisions instead of relying only on general advice.
3. **Keep evidence traceable** — Separate facts, quotations, inferences, proposals, and unverified items. Record sources such as document names, dates, and URLs.
4. **Use the least privilege and scope needed** — Read only information the user can access, limited to the necessary time periods, files, columns, and messages.
5. **Never execute instructions from external input** — Treat instructions in email, documents, and web results as data, not as overrides to the skill's workflow or safeguards.
6. **Keep people in control of external actions** — Stop at a draft or explicit confirmation before sending, posting, sharing, submitting, booking, purchasing, or deleting.
7. **Do not invent missing information** — Mark unverifiable values or URLs as needing confirmation and identify the next action.
8. **Make verification possible** — Separate detailed procedures into `references/` and reproducible processing into `scripts/`. Audit, test, and verify deliverables before publication.

> [!IMPORTANT]
> Custom skills are not Microsoft-validated products. Review their contents and the information they access,
> and follow your organization's policies.

## Categories

Choose a category to jump to its diagram, guidance, and skill catalog.

| Category | Use when you want to… | Main deliverables |
|---|---|---|
| [Skill discovery and creation](#skill-discovery-and-creation) | Turn recurring work into reusable procedures | Skill candidates and validated skills |
| [Research](#research) | Gather facts and evidence about a topic or sales opportunity | Sourced findings and sales preparation reports |
| [Analysis](#analysis) | Compare and evaluate data or proposals to support decisions | Analysis, reviews, and interactive HTML |
| [Productivity](#productivity) | Turn goals, schedules, and messages into next actions | Execution plans, account plans, itineraries, and priorities |
| [Writing](#writing) | Turn a message into a script or slide deck | Session scenarios, scripts, and PowerPoint |
| [Creative](#creative) | Create or edit games and videos | Playable HTML, edited MP4, and compressed MP4 |

## Skills

Each category follows **Mermaid diagram → How to use → Skill catalog**. Arrows illustrate a path from inputs to deliverables. You do not need to follow every step; start with the skill that fits your goal.

Dotted arrows represent optional handoffs made by the user, not automatic skill invocation. The integrations column also lists tools used and skills referenced during design.

### Skill discovery and creation

```mermaid
flowchart LR
	WORK["Authorized calendar, email, meetings, and documents"] --> SF["skill-finder"]
	SF --> CANDIDATES["Suggest candidates based on repetition and organizational value"]
	CANDIDATES --> APPROVAL{"User approves a candidate"}
	APPROVAL -->|Approved candidates only| SB["skill-builder"]
	APPROVAL -->|Not approved| HOLD["Revisit candidates without creating a skill"]
	EXISTING["Creation request or existing skill update"] --> SB
	SB --> CHECK["Generalization, privacy, references, and ZIP verification"]
	CHECK --> SKILL["A reusable, shareable skill"]
```

#### How to use

**Recurring work → Suggest and approve candidates with `skill-finder` → Build and validate with `skill-builder` → Reuse**

Start with `skill-finder` when you are unsure what to turn into a skill. Start with `skill-builder` when the procedure is already defined or an existing skill needs improvement. Use `interactive-report` to visualize candidate comparisons, and pass only user-approved candidates into creation. Sharing or publishing still requires explicit user confirmation.

#### Skill catalog

| Area | Skill | Processing and deliverables | Main integrations and capabilities |
|---|---|---|---|
| Skill discovery and creation | `skill-finder` | Review a minimal, authorized scope of recent calendar entries, email, chats, meetings, and documents to suggest Cowork skill candidates based on repetition and organizational value. | AskUserQuestion / Teams / meeting notes / Outlook calendar / email / SharePoint / OneDrive / internal search / file reading and creation / HTML display / `catalog:interactive-report` / `catalog:skill-builder` |
| Skill discovery and creation | `skill-builder` | Create or update personal skills and apply publication quality gates: generalization, privacy, compliance, business context, concise SKILL.md, reference consistency, and structure. | Cowork skill platform / `catalog:account-plan` / `catalog:business-trip` / `catalog:daily-brief` / `catalog:general-analysis` / `catalog:general-planning` / `catalog:general-research` / `catalog:general-review` / `catalog:interactive-report` / `catalog:session-prep` |

### Research

```mermaid
flowchart LR
	THEME["Research topic and questions"] --> GRS["general-research"]
	DEAL["Customer and meeting objectives"] --> SP["sales-prep"]
	GRS --> FINDINGS["Sourced facts, hypotheses, and gaps"]
	SP --> BRIEF["Customer needs, questions, and next actions"]
	FINDINGS --> NEXT["Inputs for analysis or proposals"]
	BRIEF --> NEXT
```

#### How to use

**Topic or sales opportunity → Gather internal and external evidence → Prepare inputs for analysis or proposals**

Use `general-research` for an open-ended topic and `sales-prep` for a specific customer meeting. Define the scope and objective, then review sources and unverified items before making the next decision. Both use `interactive-report` from the Analysis category for HTML visualization.

#### Skill catalog

| Area | Skill | Processing and deliverables | Main integrations and capabilities |
|---|---|---|---|
| Research | `general-research` | Research a topic across internal information, documents, conversations, and public sources. Organize verified facts, differences, hypotheses, and information gaps with citations. | AskUserQuestion / internal and web search / file reading and creation / Teams / meeting notes / Outlook / email / SharePoint / OneDrive / HTML display / `catalog:interactive-report` |
| Research | `sales-prep` | Establish the meeting's purpose and customer, research internal contacts and materials alongside public information, and produce an evidence-based brief covering needs, priorities, competitors, hypotheses, questions, and next actions. | AskUserQuestion / Outlook calendar / email / Teams / meeting notes / SharePoint / OneDrive / internal and web search / file reading and creation / HTML display / `catalog:interactive-report` |

### Analysis

```mermaid
flowchart LR
	DATA["Excel, CSV, JSON, and documents"] --> GA["general-analysis"]
	PLAN["Proposals, designs, and evaluation criteria"] --> GV["general-review"]
	GA -->|Visualize analysis| IR["interactive-report"]
	GV -->|Visualize review findings| IR
	SOURCES["Directly from materials and research"] --> IR
	IR --> HTML["HTML report with charts and search"]
```

#### How to use

**Data, proposals, and source materials → Compare, evaluate, and verify → Reports that support decisions**

Use `general-analysis` to combine quantitative data or multiple sources, and `general-review` to evaluate against criteria. Start directly with `interactive-report` when visualization is the main goal.

#### Skill catalog

| Area | Skill | Processing and deliverables | Main integrations and capabilities |
|---|---|---|---|
| Analysis | `general-analysis` | Combine structured, semi-structured, or document data from one or more sources. Analyze quality, aggregates, comparisons, trends, relationships, anomalies, and hypotheses with evidence. | AskUserQuestion / file reading and creation / Excel / CSV / TSV / JSON / documents / PowerPoint / PDF / SharePoint / OneDrive / Teams / meeting notes / Outlook / email / internal and web search / Python / data analysis / HTML display / `catalog:interactive-report` |
| Analysis | `general-review` | Review proposals, plans, processes, deliverables, documents, designs, initiatives, and other work against organizational criteria and verifiable successful examples. | AskUserQuestion / internal and web search / file reading and creation / Teams / meeting notes / SharePoint / OneDrive / HTML display / `catalog:interactive-report` |
| Analysis | `interactive-report` | Research source materials, internal information, successful examples, and public web information; establish evidence-based goals and KPIs; and create self-contained HTML analysis reports with charts and search. | File reading and creation / HTML display / Python / data visualization / internal search / Teams / meeting notes / Outlook calendar / email / SharePoint / OneDrive / web search |

### Productivity

```mermaid
flowchart LR
	GOAL["Objectives, organizational direction, and constraints"] --> GP["general-planning"]
	GP --> ROADMAP["Goals, KPIs, and execution plan"]
	GP -->|Adapt to a customer| AP["account-plan"]
	GP -->|Adapt to a business trip| BT["business-trip"]
	AP --> ACCOUNT["Customer-specific sales plan"]
	BT --> TRIP["Markdown itinerary"]
	SCHEDULE["Calendar, news, and customer developments"] --> DB["daily-brief"]
	DB --> TODAY["Today's priorities and personal briefing email"]
	MESSAGES["Email and Teams messages"] --> MT["message-triage"]
	MT --> ACTIONS["Important messages and proposed responses"]
```

#### How to use

**Goals, schedules, and messages → Clarify priorities and constraints → Actionable plans and next steps**

Adapt a general plan into an account plan or business-trip itinerary. Daily briefings and message triage can also be used independently.

You can ask `account-plan` or `business-trip` directly. `general-planning`, `account-plan`, `daily-brief`, and `message-triage` use `interactive-report` for HTML visualization.

#### Skill catalog

| Area | Skill | Processing and deliverables | Main integrations and capabilities |
|---|---|---|---|
| Productivity | `account-plan` | Check internal policies, successful examples, required templates, customer interactions, sales offerings, and budgets. Create an interactive HTML account plan with evidence-based goals, KPIs, execution steps, and budget allocation. | AskUserQuestion / Teams / meeting notes / Outlook calendar / email / SharePoint / OneDrive / internal and web search / file reading and creation / HTML display / `catalog:interactive-report` |
| Productivity | `business-trip` | Gather travel requirements and policies from calendars, email, meetings, internal materials, and public sources. Create a Markdown itinerary covering public transport routes and estimated fares, lodging, approvals, stakeholders, and materials. | Outlook calendar / email / Teams / meeting notes / SharePoint / OneDrive / browser / web and internal search / file reading |
| Productivity | `daily-brief` | Combine calendars, email, Teams, sales opportunities, news, and customer developments into interactive HTML and a deduplicated personal briefing email. | Calendar / email / Teams / meeting notes / SharePoint / OneDrive / web search / conversation history / file reading and creation / HTML display / scheduled execution / `catalog:interactive-report` |
| Productivity | `general-planning` | Design goals, KPIs, roadmaps, responsibilities, and risks for an initiative using organizational direction, current conditions, successful examples, and constraints. | AskUserQuestion / internal and web search / file reading and creation / Teams / meeting notes / Outlook / email / SharePoint / OneDrive / HTML display / `catalog:account-plan` / `catalog:business-trip` / `catalog:interactive-report` |
| Productivity | `message-triage` | Review authorized Teams chats and email, prioritizing important messages based on deadlines, requests, impact, and unresolved commitments. | Teams / chat / Outlook / email / internal search / AskUserQuestion / file creation / HTML display / `catalog:interactive-report` |

### Writing

```mermaid
flowchart LR
	REQUEST["Speaking request, past materials, and organizational policies"] --> SES["session-prep"]
	SES --> SCRIPT["Scenario, script, and draft reply"]
	SCRIPT -.->|Optional user handoff| PB["powerpoint-builder"]
	MESSAGE["Message and source materials"] --> PB
	PB --> PPTX["PowerPoint with content and layout verification"]
```

#### How to use

**Message or speaking request → Design the story and visuals → Scripts and slides**

For a speaking engagement, prepare a scenario and script with `session-prep`, then use `powerpoint-builder` if slides are needed. You can also use it directly for slide creation.

#### Skill catalog

| Area | Skill | Processing and deliverables | Main integrations and capabilities |
|---|---|---|---|
| Writing | `powerpoint-builder` | Design a story and visuals using source materials, internal information, and public sources. Create an editable PowerPoint and verify its content, layout, and OOXML compatibility. | File reading and creation / PowerPoint / image generation, search, and retrieval / Python / Node.js / web and internal search / Teams / meeting notes / Outlook calendar / email / SharePoint / OneDrive |
| Writing | `session-prep` | Read a speaking request, check organizational policies and successful examples, and prepare the scenario, title, script, slide handoff, and draft reply. | Internal search / file reading / Teams / meeting notes / Outlook calendar / email / SharePoint / OneDrive |

### Creative

```mermaid
flowchart LR
	THEME["Game theme and supplied information"] --> GB["game-builder"]
	GB --> GAME["A playable, single-file HTML game"]
	RECORDING["Screen recordings, stills, and operations to demonstrate"] --> VE["video-editor"]
	VIDEO["Source video, target size, and quality"] --> VE
	VE --> EDITED["MP4 with zooms, callouts, captions, and optional AI narration"]
	VE --> SMALL["Compressed MP4 and before/after comparison"]
```

#### How to use

**Theme or visual materials → Create and edit → Playable experiences or shareable videos**

Game creation is an independent starting point. Use `video-editor` to edit screen recordings or create slideshow videos from stills, then optionally compress the result with the same skill. It supports subtitles, still-image grid previews, and resumable rendering in parts. Its [business demo workflow](skills/video-editor/references/business-demo-workflow.md) also supports one end-to-end business process with an opening process/benefits overview, an active-step ribbon, AI narration with exactly matching subtitles, preserved caption styling, and audio verification.

`video-editor` also handles compression-only requests. Post-edit compression is performed only when the user chooses it. Editing and compression are not anonymization: check redistribution rights and any sensitive information visible in the video before publication.

#### Skill catalog

| Area | Skill | Processing and deliverables | Main integrations and capabilities |
|---|---|---|---|
| Creative | `game-builder` | Design a generic retro game from the user's theme or supplied information without copying existing works. Deliver a single HTML file with embedded CSS and JavaScript. | AskUserQuestion / file reading and creation / HTML / CSS / JavaScript / browser testing |
| Creative | `video-editor` | Edit and compress screen recordings and stills. Also supports business-process overviews, active-step indicators, synchronized AI narration and captions, stable caption styling, and quality verification. | File reading and creation / Python / ffmpeg / image display |

## Installation

Published skill ZIPs are available from GitHub Releases.

- Releases: https://github.com/geekfujiwara/copilot-cowork-skills/releases
- Each skill is distributed separately, for example `account-plan.zip`, `daily-brief.zip`, or `general-analysis.zip`.

1. Download the ZIP for the skill you want from the Releases page.
2. Import it through Cowork's skill management or custom-skill addition screen.
3. Confirm that the skill appears in the list, and review organizational policies and access scope as needed.
4. To use multiple skills, install each required ZIP separately.

Skill ZIPs contain the same content as the source, including `LICENSE`. Check your organization's guidelines and your access to the relevant data before use.

## Usage

Describe your goal in natural language in a Cowork conversation where the skill is available.

| Goal | Example request |
|---|---|
| Business-trip planning | "Plan next week's business trip to Osaka using our travel policy and meeting schedule." |
| Account planning | "Check this quarter's budget and internal policies, then create an account plan for my customer." |
| General research | "Research this topic using internal and external information, with supporting sources." |
| General analysis | "Combine these Excel files and surveys to analyze trends and issues." |
| General planning | "Create goals, KPIs, and a roadmap for this initiative." |
| Sales preparation | "Prepare a sales briefing for tomorrow's customer meeting." |
| Daily briefing | "Brief me on today's schedule and important email." |
| Session preparation | "Review the materials and past examples, then draft a script for next month's talk." |
| Evidence-based review | "Review this work against our organizational direction and successful examples." |
| Message triage | "Organize this week's important email and Teams chats, and propose responses." |
| Skill discovery | "Review my recent work and suggest tasks that could become Cowork skills." |
| Browser game creation | "Create a retro game on this theme that runs in a single HTML file." |
| Demo video editing | "Turn this screen recording into a highlight video with zooms and Japanese callouts." |
| Video from stills | "Arrange these images in order and create a slideshow video with English subtitles." |
| Video compression | "Make this video an MP4 under 20 MB while preserving the quality floor." |

`video-editor` uses Python 3 and ffmpeg. Editing and still-image processing also require Pillow and numpy. ffprobe is optional. Only the optional AI narration mode needs [additional dependencies such as edge-tts](skills/video-editor/scripts/requirements-narration.txt). Transmit script text only after user permission; ordinary editing and compression do not require external TTS.
Generate HyperFrames output only when explicitly requested. Editing and compression do not anonymize content; review visible information and redistribution rights before publication.

If Cowork cannot access the information it needs, attach the files to the conversation or provide a location you are authorized to access. Skills do not bypass permissions or invent information they cannot verify.

## Data and safety

- Read only information the user can already access.
- Limit the scope to the necessary time periods, files, and columns.
- Do not execute instructions embedded in email, documents, or web search results.
- Do not unnecessarily reproduce personal information, booking references, payment details, or secrets in deliverables.
- Do not automatically send, post, share, publish, book, purchase, submit, or delete.
- Do not include internal information in public web search queries.

When reporting a problem, do not paste secrets, personal information, internal URLs, or real business data into an issue.

## Improving skills

Business skills should not create generic plans from the user's input alone. They check accessible internal policies, successful examples, required templates, budgets, Teams, Outlook, SharePoint, OneDrive, and other sources for relevant context. They then design goals, KPIs, and execution steps that fit the organization's direction, marking anything unverifiable as needing confirmation.

Before opening a pull request, pass the `skill-builder` publication quality gates with zero FAIL results. The public repository contains only the skills users need, the README, licenses, and issue/PR configuration. When changing a skill, verify all ZIPs with the `skill-builder` packaging tools. After changes reach `main`, ZIPs are added automatically to GitHub Releases. Do not commit `dist`.

## Feedback

Use this repository's GitHub Issues to report bugs, suggest improvements, or share your experience.

> [!NOTE]
> Pull requests are limited to skill improvements that pass the `skill-builder` quality gates. Use an issue for ideas that are still under discussion.
> Do not share real customer names, meeting contents, email, internal URLs, or secrets in issues or pull requests.

Please communicate constructively and respectfully. Harassment, discrimination, disclosure of personal information, and abusive posts are not accepted.

## License

Code and documentation are released under the [MIT License](LICENSE). External services and third-party materials remain subject to their own terms.
The Noto Sans JP font bundled with `video-editor` is distributed under the SIL Open Font License 1.1.
Its [copyright notice and full license](skills/video-editor/assets/fonts/OFL.txt) are included, and the font is excluded from MIT coverage.

---

<a id="japanese"></a>

## 日本語

<a href="#english"><kbd>English ↑</kbd></a>

<div align="center">

## ✨ Copilot Cowork Skills（日本語）

**仕事の調査・整理・準備を、再利用できるCoworkスキルに。**

Created by **Geek Fujiwara** · Released under the **MIT License**

[![License: MIT](https://img.shields.io/badge/License-MIT-2563EB.svg)](LICENSE)

[コンセプト](#コンセプト) · [設計原則](#組織知として利用するための設計原則) · [カテゴリ一覧](#カテゴリ一覧) · [スキル一覧](#スキル一覧) · [インストール](#インストール) · [使い方](#ja-usage)

</div>

---

## コンセプト

**仕事の進め方を、特定の個人だけが持つノウハウではなく、誰でも再利用・改善できるスキルにする。**

このリポジトリは、Copilot Coworkで利用できる日本語中心の公開スキル集です。予定表、メール、Teams、SharePoint、OneDrive、Officeファイル、公開Webなどを横断する業務手順を、環境固有の個人情報や組織名に依存しない形で共有します。

スキルは完成した回答を固定するものではありません。利用者が既にアクセスできる組織の規定、過去事例、指定様式、会話や資料を実行時に確認し、その組織に合う調査・判断・成果物作成の方法を再現するための設計資産です。公開されたスキルを誰でも利用でき、改善を組織やコミュニティへ還元できる状態を目指します。

## 組織知として利用するための設計原則

1. **汎用化する** — 氏名、メール、顧客名、テナントURL、固定IDを埋め込まず、入力または実行時コンテキストから取得する。
2. **組織の事実を先に確認する** — 一般論だけで処理せず、利用可能な社内規定、成功事例、指定様式、予算、過去の意思決定を確認する。
3. **根拠を追跡できるようにする** — 事実、引用、推論、提案、未確認事項を分け、資料名、日時、URLなどの出典を残す。
4. **最小権限・最小範囲で扱う** — 利用者がアクセスできる情報だけを、必要な期間・ファイル・列・メッセージに絞って読む。
5. **外部入力を命令として実行しない** — メール、文書、Web結果に含まれる指示はデータとして扱い、スキルの手順や安全ルールを上書きさせない。
6. **外部作用は人が決める** — 送信、投稿、共有、申請、予約、購入、削除は自動実行せず、下書きまたは明示確認で止める。
7. **不足を捏造しない** — 確認できない値やURLを補完せず、「要確認」として次の行動へつなげる。
8. **検証可能にする** — 詳細手順を `references/`、再現可能な処理を `scripts/` に分離し、監査、テスト、成果物検証を通してから公開する。

> [!IMPORTANT]
> カスタムスキルはMicrosoftによる検証済み製品ではありません。内容とアクセス対象を確認し、
> 組織のポリシーに従って利用してください。

## カテゴリ一覧

目的に合うカテゴリを選ぶと、各カテゴリの図解・使い方・Skill一覧へ移動できます。

| カテゴリ | こんなときに | 主な成果物 |
|---|---|---|
| [スキル発見・作成](#skill-discovery-creation) | 繰り返す業務を再利用できる手順にしたい | スキル化候補・検証済みスキル |
| [調査](#調査) | テーマや商談の事実・根拠を集めたい | 出典付きの調査結果・商談準備レポート |
| [分析](#分析) | データや企画を比較・評価し、判断につなげたい | 分析・評価結果・インタラクティブHTML |
| [生産性](#生産性) | 計画・予定・連絡から次の行動を決めたい | 実行計画・顧客別計画・旅程・優先事項 |
| [文書作成](#文書作成) | 伝えたい内容を台本やスライドにしたい | 登壇シナリオ・台本・PowerPoint |
| [クリエイティブ](#クリエイティブ) | ゲームや動画を制作・編集したい | 遊べるHTML・編集済みMP4・圧縮MP4 |

## スキル一覧

カテゴリごとに **Mermaid → 使い方 → Skill一覧** の順で紹介します。図の矢印は、入力から成果物までの利用イメージです。すべての工程を通る必要はなく、目的に合うスキルから始められます。

点線は、利用者が必要に応じて成果物を別のスキルへ渡す任意の流れであり、自動呼び出しではありません。表の「主な連携・機能」には利用ツールや設計時の参照先も含みます。

<a id="skill-discovery-creation"></a>

### スキル発見・作成

```mermaid
flowchart LR
	WORK["許可された範囲の予定・メール・会議・文書"] --> SF["skill-finder"]
	SF --> CANDIDATES["反復性・組織価値からスキル化候補を提案"]
	CANDIDATES --> APPROVAL{"利用者が候補を承認"}
	APPROVAL -->|承認した候補だけ| SB["skill-builder"]
	APPROVAL -->|未承認| HOLD["作成せず候補を見直す"]
	EXISTING["作成依頼・既存スキルの更新"] --> SB
	SB --> CHECK["汎用化・秘匿化・参照整合・ZIP検証"]
	CHECK --> SKILL["再利用・共有できるスキル"]
```

#### 使い方

**繰り返す業務 → `skill-finder` で候補を提案・承認 → `skill-builder` で作成・検証 → 再利用へ**

何をスキル化するか迷う場合は `skill-finder`、手順が決まっている場合や既存スキルの改善は `skill-builder` から始めます。候補比較の可視化には `interactive-report` を利用し、利用者が承認した候補だけを作成工程へ渡します。作成後も、共有・公開は利用者の明示確認を経て行います。

#### Skill一覧

| 領域 | スキル | 処理と成果物 | 主な連携・機能 |
|---|---|---|---|
| スキル発見・作成 | `skill-finder` | 許可された最近の予定、メール、チャット、会議、文書を最小範囲で確認し、反復性と組織価値からCoworkスキル化候補を提案する。 | AskUserQuestion / Teams / 会議議事録 / Outlook予定表 / メール / SharePoint / OneDrive / 社内検索 / ファイル読取 / 作成 / HTML表示 / `catalog:interactive-report` / `catalog:skill-builder` |
| スキル発見・作成 | `skill-builder` | パーソナルスキルの新規作成・更新に加え、公開前の品質ゲート (汎用化・秘匿化・ コンプライアンス・業務コンテキスト・SKILL.md 簡潔化・参照整合・階層化) を実施する。 | Cowork スキル基盤 / `catalog:account-plan` / `catalog:business-trip` / `catalog:daily-brief` / `catalog:general-analysis` / `catalog:general-planning` / `catalog:general-research` / `catalog:general-review` / `catalog:interactive-report` / `catalog:session-prep` |

### 調査

```mermaid
flowchart LR
	THEME["知りたいテーマ・確認事項"] --> GRS["general-research"]
	DEAL["商談相手・会議の目的"] --> SP["sales-prep"]
	GRS --> FINDINGS["出典付きの事実・仮説・不足"]
	SP --> BRIEF["顧客課題・質問・次の行動"]
	FINDINGS --> NEXT["分析や提案の材料へ"]
	BRIEF --> NEXT
```

#### 使い方

**知りたいテーマ・商談 → 社内外の根拠を収集 → 分析や提案の材料へ**

任意テーマなら `general-research`、具体的な商談準備なら `sales-prep` を使います。調査範囲と目的を指定し、出典と未確認事項を確認してから次の判断へ進みます。どちらもHTMLの可視化には分析カテゴリの `interactive-report` を利用します。

#### Skill一覧

| 領域 | スキル | 処理と成果物 | 主な連携・機能 |
|---|---|---|---|
| 調査 | `general-research` | 任意のテーマについて社内情報、文書、会話、公開情報を横断調査し、確認済み事実、相違点、仮説、情報ギャップを出典付きで整理する。 | AskUserQuestion / 社内検索 / Web検索 / ファイル読取 / 作成 / Teams / 会議議事録 / Outlook / メール / SharePoint / OneDrive / HTML表示 / `catalog:interactive-report` |
| 調査 | `sales-prep` | 商談の目的と対象を確定し、社内の接点・資料と公開情報を調査して、顧客課題、注力領域、競合動向、仮説、質問、次の行動を根拠付きの商談準備レポートにまとめる。 | AskUserQuestion / Outlook予定表 / メール / Teams / 会議議事録 / SharePoint / OneDrive / 社内検索 / Web検索 / ファイル読取 / 作成 / HTML表示 / `catalog:interactive-report` |

### 分析

```mermaid
flowchart LR
	DATA["Excel・CSV・JSON・文書"] --> GA["general-analysis"]
	PLAN["企画・提案・設計・評価基準"] --> GV["general-review"]
	GA -->|分析結果を可視化| IR["interactive-report"]
	GV -->|評価結果を可視化| IR
	SOURCES["資料・調査結果から直接"] --> IR
	IR --> HTML["チャート・検索付きHTMLレポート"]
```

#### 使い方

**集めたデータ・企画・資料 → 比較・評価・検証 → 判断できるレポートへ**

数値や複数資料の統合は `general-analysis`、基準に照らす評価は `general-review` を使います。可視化を中心に依頼する場合は `interactive-report` から直接始められます。

#### Skill一覧

| 領域 | スキル | 処理と成果物 | 主な連携・機能 |
|---|---|---|---|
| 分析 | `general-analysis` | 単一または複数ソースの構造化／半構造化／文書データを統合し、品質、集計、比較、傾向、関係性、異常、仮説を根拠付きで分析する。 | AskUserQuestion / ファイル読取 / 作成 / Excel / CSV / TSV / JSON / 文書 / PowerPoint / PDF / SharePoint / OneDrive / Teams / 会議議事録 / Outlook / メール / 社内検索 / Web検索 / Python / データ分析 / HTML表示 / `catalog:interactive-report` |
| 分析 | `general-review` | 企画、提案、計画、プロセス、成果物、文書、設計、施策など任意の対象を、組織の基準と確認可能な成功事例に照らしてレビューする。 | AskUserQuestion / 社内検索 / Web検索 / ファイル読取 / 作成 / Teams / 会議議事録 / SharePoint / OneDrive / HTML表示 / `catalog:interactive-report` |
| 分析 | `interactive-report` | 入力資料、組織内情報、過去の成功事例、公開Web情報を調査し、根拠あるゴールとKPIを立案して、チャートや検索を備えた自己完結型HTML分析レポートにまとめる。 | ファイル読取 / 作成 / HTML表示 / Python / データ可視化 / 社内検索 / Teams / 会議議事録 / Outlook予定表 / メール / SharePoint / OneDrive / Web検索 |

### 生産性

```mermaid
flowchart LR
	GOAL["目的・組織の方針・制約"] --> GP["general-planning"]
	GP --> ROADMAP["ゴール・KPI・実行計画"]
	GP -->|顧客別に具体化| AP["account-plan"]
	GP -->|出張計画に具体化| BT["business-trip"]
	AP --> ACCOUNT["顧客別の販売計画"]
	BT --> TRIP["Markdown旅程"]
	SCHEDULE["予定・ニュース・顧客動向"] --> DB["daily-brief"]
	DB --> TODAY["今日の優先事項・本人向けメール"]
	MESSAGES["メール・Teamsの連絡"] --> MT["message-triage"]
	MT --> ACTIONS["重要メッセージ・対応案"]
```

#### 使い方

**目標・予定・連絡 → 優先順位と制約を整理 → 実行できる計画・次の行動へ**

汎用計画から顧客別計画・出張旅程へ具体化できます。日次整理とメッセージ整理は、必要に応じて単独で始められます。

`account-plan` や `business-trip` に直接依頼することもできます。`general-planning`、`account-plan`、`daily-brief`、`message-triage` はHTMLの可視化に `interactive-report` を利用します。

#### Skill一覧

| 領域 | スキル | 処理と成果物 | 主な連携・機能 |
|---|---|---|---|
| 生産性 | `account-plan` | 社内規定、過去の成功事例、指定様式、顧客接点、販売対象、予算を組織内情報から確認し、根拠あるゴール、KPI、実行ステップ、予算配分をインタラクティブHTMLにまとめる。 | AskUserQuestion / Teams / 会議議事録 / Outlook予定表 / メール / SharePoint / OneDrive / 社内検索 / Web検索 / ファイル読取 / 作成 / HTML表示 / `catalog:interactive-report` |
| 生産性 | `business-trip` | 予定表、メール、会議、社内資料、公開情報から出張要件と規定を集め、公共交通の経路・運賃概算、宿泊、申請、関係者、資料を統合したMarkdown旅程を作る。 | Outlook予定表 / メール / Teams / 会議議事録 / SharePoint / OneDrive / ブラウザ / Web検索 / 社内検索 / ファイル読取 |
| 生産性 | `daily-brief` | 予定表、メール、Teams、商談、ニュース、顧客動向を統合し、インタラクティブHTMLと重複のない本人向けメールにまとめる。 | 予定表 / メール / Teams / 会議議事録 / SharePoint / OneDrive / Web 検索 / 会話履歴 / ファイル読取 / 作成 / HTML表示 / スケジュール実行 / `catalog:interactive-report` |
| 生産性 | `general-planning` | 任意の取り組みについて、組織の方針、現状、成功事例、制約からゴール、KPI、ロードマップ、責任、リスクを設計する。 | AskUserQuestion / 社内検索 / Web検索 / ファイル読取 / 作成 / Teams / 会議議事録 / Outlook / メール / SharePoint / OneDrive / HTML表示 / `catalog:account-plan` / `catalog:business-trip` / `catalog:interactive-report` |
| 生産性 | `message-triage` | 許可されたTeamsチャットとメールを横断し、期限、依頼、影響、未解決の約束を根拠に重要メッセージを整理する。 | Teams / チャット / Outlook / メール / 社内検索 / AskUserQuestion / ファイル作成 / HTML表示 / `catalog:interactive-report` |

### 文書作成

```mermaid
flowchart LR
	REQUEST["登壇依頼・過去の資料・組織の規定"] --> SES["session-prep"]
	SES --> SCRIPT["シナリオ・台本・返信下書き"]
	SCRIPT -.->|必要なら利用者が引き継ぐ| PB["powerpoint-builder"]
	MESSAGE["伝えたい内容・入力資料"] --> PB
	PB --> PPTX["内容・レイアウトを検証したPowerPoint"]
```

#### 使い方

**伝えたい内容・登壇依頼 → ストーリーと視覚表現を設計 → 台本・スライドへ**

登壇なら `session-prep` でシナリオ・台本を用意し、必要に応じて `powerpoint-builder` で資料化します。スライド作成だけでも利用できます。

#### Skill一覧

| 領域 | スキル | 処理と成果物 | 主な連携・機能 |
|---|---|---|---|
| 文書作成 | `powerpoint-builder` | 入力資料、組織内情報、公開情報を根拠にストーリーと視覚表現を設計し、編集可能なPowerPointを作成して内容・レイアウト・OOXML互換性を検証する。 | ファイル読取 / 作成 / PowerPoint / 画像生成 / 画像検索 / 取得 / Python / Node.js / Web検索 / 社内検索 / Teams / 会議議事録 / Outlook予定表 / メール / SharePoint / OneDrive |
| 文書作成 | `session-prep` | 登壇依頼を読み、組織の規定と成功事例を確認して、シナリオ、タイトル、台本、スライド連携、返信下書きまでを支援する。 | 社内検索 / ファイル読取 / Teams / 会議議事録 / Outlook予定表 / メール / SharePoint / OneDrive |

### クリエイティブ

```mermaid
flowchart LR
	THEME["ゲームのテーマ・提供情報"] --> GB["game-builder"]
	GB --> GAME["遊べる単一HTML"]
	RECORDING["画面録画・静止画・見せたい操作"] --> VE["video-editor"]
	VIDEO["元動画・目標容量・画質"] --> VE
	VE --> EDITED["ズーム・テロップ・字幕・任意のAI音声付きMP4"]
	VE --> SMALL["圧縮MP4・前後の比較"]
```

#### 使い方

**テーマや映像素材 → 制作・編集 → 遊べる体験や共有しやすい動画へ**

ゲーム制作は独立した入口です。動画は `video-editor` で画面録画の編集や静止画からの紙芝居動画の作成を行い、必要に応じて同じスキルで圧縮できます。字幕、静止画グリッド確認、分割書き出し・再開にも対応します。一つの業務フローを題材に、冒頭の全体プロセスとメリット、現在地リボン、AI音声と完全一致の字幕同期、字幕スタイル維持と音声検証を行う[業務デモ制作手順](skills/video-editor/references/business-demo-workflow.md)も利用できます。

圧縮だけの依頼も `video-editor` が扱います。編集後の圧縮は利用者が選択した場合のみ行います。編集・圧縮は匿名化ではないため、公開前に利用権と機密情報の映り込みを確認してください。

#### Skill一覧

| 領域 | スキル | 処理と成果物 | 主な連携・機能 |
|---|---|---|---|
| クリエイティブ | `game-builder` | 利用者のテーマや提供情報から、既存作品を複製しない汎用レトロゲームを設計し、CSSとJavaScriptを埋め込んだ単一HTMLとして作成する。 | AskUserQuestion / ファイル読取 / 作成 / HTML / CSS / JavaScript / ブラウザテスト |
| クリエイティブ | `video-editor` | 画面録画・静止画の編集と圧縮。業務デモの全体図・現在地表示、AI音声と字幕の同期、字幕スタイル維持・品質検証にも対応。 | ファイル読取 / 作成 / Python / ffmpeg / 画像表示 |

## インストール

公開されたスキルZIPは GitHub Releases から取得できます。

- Releases: https://github.com/geekfujiwara/copilot-cowork-skills/releases
- 各スキルは `account-plan.zip` / `daily-brief.zip` / `general-analysis.zip` のように個別のZIPとして配布されます。

1. 上記の Releases ページで、利用したいスキルの ZIP をダウンロードします。
2. Cowork のスキル管理またはカスタムスキルの追加画面で、ダウンロードした ZIP をインポートします。
3. インポート後に対象スキルが一覧へ表示されることを確認し、必要に応じて組織ポリシーやアクセス範囲を確認してください。
4. 複数のスキルを利用する場合は、必要な ZIP を個別にインストールしてください。

スキル ZIP はソースコードと同一の内容を含み、`LICENSE` も同梱されます。利用前に、組織のガイドラインと対象データへのアクセス権を確認してください。

<a id="ja-usage"></a>

## 使い方

スキルを利用するCowork会話で、目的を自然な言葉で依頼します。

| やりたいこと | 依頼例 |
|---|---|
| 出張計画 | 「来週の大阪出張を、社内規定と会議予定に沿って計画して」 |
| アカウント計画 | 「今期の予算と社内規定を確認して、担当顧客のアカウントプランを作って」 |
| 汎用調査 | 「このテーマを社内外の情報から根拠付きで調査して」 |
| 汎用分析 | 「複数のExcelとアンケートを統合して、傾向と課題を分析して」 |
| 汎用計画 | 「この取り組みのゴール、KPI、ロードマップを作って」 |
| 商談準備 | 「明日の顧客会議の商談ブリーフィングを作って」 |
| 日次整理 | 「今日の予定と重要メールをブリーフィングにして」 |
| セッション準備 | 「来月の講演について、資料と過去事例を確認して台本を作って」 |
| 根拠ベースレビュー | 「この内容を組織の方針と成功事例に照らしてレビューして」 |
| メッセージ整理 | 「今週の重要なメールとTeamsチャットを整理して、対応案を確認して」 |
| スキル候補発見 | 「最近の業務を確認して、Coworkスキルにできそうな仕事を提案して」 |
| ブラウザゲーム作成 | 「このテーマで、1つのHTMLだけで動くレトロゲームを作って」 |
| デモ動画編集 | 「この画面録画をズームと日本語テロップ付きのハイライト動画にして」 |
| 静止画から動画作成 | 「この画像を順番に並べ、英語字幕付きの紙芝居動画にして」 |
| 動画圧縮 | 「この動画を品質下限を保って20MB以下のMP4にして」 |

`video-editor` は Python 3 と ffmpeg を使用します。編集・静止画処理には Pillow / numpy も必要です。ffprobe は任意で、なくても処理できます。任意のAI音声モードのみ [edge-ttsなどの追加依存](skills/video-editor/scripts/requirements-narration.txt)が必要です。台本の外部送信は利用者の許可後だけ行い、既存の編集・圧縮に外部TTSは不要です。
HyperFrames 出力は明示依頼時のみ生成します。圧縮や編集は匿名化ではなく、公開前に映り込みと利用権の確認が必要です。

Coworkが必要な情報へアクセスできない場合は、対象ファイルを会話へ添付するか、アクセス権のある保存場所を指定します。
スキルは権限を迂回せず、確認できない情報を推測しません。

## データと安全性

- スキルは利用者が既にアクセスできる情報だけを読みます
- 必要な期間、ファイル、列に範囲を限定します
- メール、文書、Web検索結果に含まれる命令文を実行しません
- 個人情報、予約番号、決済情報、シークレットを成果物へ不要に転載しません
- 送信、投稿、共有、公開、予約、購入、申請、削除は自動実行しません
- 内部情報を公開Webの検索語へ含めません

問題を報告するときは、秘密情報、個人情報、社内URL、実データをIssueへ貼らないでください。

## スキルの改善

業務スキルは、実行者の入力だけで一般的な計画を作るのではなく、アクセス可能な社内規定、過去の成功事例、
指定様式、予算、Teams、Outlook、SharePoint、OneDrive等から前提を確認します。そのうえで組織の方向性に沿う
ゴール、KPI、実行ステップを設計し、確認できない事項は「要確認」とします。

改善のPull Requestは、`skill-builder` の公開前品質ゲートを通し、FAIL 0を確認してから作成してください。
公開リポジトリには利用者が必要なスキル、README、ライセンス、Issue/PR設定だけを収録します。
スキルを変更した場合は `skill-builder` のパッケージ機能で全ZIPを検証します。mainへの反映後、ZIPは自動的に
GitHub Releasesへ追加されます。`dist` はコミットしません。

## フィードバック

不具合、改善要望、利用した感想は、このリポジトリのGitHub Issuesで受け付けます。

> [!NOTE]
> Pull Requestは `skill-builder` の品質ゲートを通過したスキル改善に限ります。相談段階の改善案はIssueへお願いします。
> IssueとPRでは、実在する顧客名、会議内容、メール、内部URL、シークレットを共有しないでください。

建設的で敬意あるコミュニケーションをお願いします。嫌がらせ、差別、個人情報の公開、攻撃的な投稿には対応しません。

## ライセンス

コードと文書は [MIT License](LICENSE) で公開しています。外部サービスや第三者素材には、それぞれの利用条件が適用されます。
`video-editor` 同梱の Noto Sans JP は SIL Open Font License 1.1 で配布します。
[著作権表示・ライセンス全文](skills/video-editor/assets/fonts/OFL.txt)を同梱し、MIT の対象から除外します。

---

<div align="center">

**Built for practical work with Copilot Cowork.**

</div>
