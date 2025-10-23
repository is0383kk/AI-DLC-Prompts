# AI-Driven Development Lifecycle (AI-DLC) Prompts

This repository contains prompts for product development following the "[AI-Driven Development Lifecycle (AI-DLC)](https://prod.d13rzhkk8cj2z0.amplifyapp.com/)" process proposed by Amazon Web Services.

- https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/

Prompt execution is designed with the assumption of **AI agent interaction such as Amazon Q developer CLI, Claude Code, or Codex CLI**.

# 1. Overview

This prompt collection consists of the following 5 phases:

1. **User Story Planning** - Define requirements as user stories
2. **Unit of Work Planning** - Break down user stories into implementable work units
3. **Domain Model Design Planning** - Design domain models for business logic
4. **Code Implementation Planning** - Implement source code from domain models
5. **Architecture Component Planning** - Build architecture to operate the implementations

## ■ Prompt Structure

```
├── 01-user-story-planning.md          # User story creation prompt
├── 02-unit-of-work-planning.md       # Work unit division prompt
├── 03-domain-model-planning.md        # Domain model design prompt
├── 04-domain-to-code-planning.md      # Code implementation prompt
└── 05-architecture-component-planning.md  # Architecture component creation prompt

```

# 2. Usage

## ■ Basic Work Flow

1. **Select Prompt**: Choose the prompt file according to the development phase
2. **Input to AI Assistant**: Input the selected prompt to the AI assistant
3. **Create Work Plan**: AI creates a work plan document
4. **Answer Questions**: Answer questions in the plan document
5. **Approve Plan**: Review and approve the work plan
6. **Step-by-Step Execution**: AI executes step by step according to the plan

## ■ Step 2: User Story Creation (`01-user-story-planning.md`)

**Role**: Product Owner
**Purpose**: Create clear user stories for the target system

1. Describe what you want to create in `01-user-story-planning.md` and execute the prompt in the file
2. A work plan document for user story creation is created: `docs/inception/01-user-story/user-story-plan.md`
3. Answer and save the questions listed in `docs/inception/01-user-story/user-story-plan.md`
4. Instruct the AI agent to create user stories according to `docs/inception/01-user-story/user-story-plan.md`
5. Work breakdown files related to user stories are created in `docs/inception/01-user-story/result`

## ■ Step 2. Unit of Work Division (`02-unit-of-work-planning.md`)

**Role**: Software Architect
**Purpose**: Divide user stories into work units that can be implemented in parallel

1. Execute the prompt in `02-unit-of-work-planning.md`
2. A work plan document for dividing user stories is created: `docs/inception/02-unit-of-work/units-plan.md`
3. Answer and save the questions listed in `docs/inception/02-unit-of-work/units-plan.md`
4. Instruct the AI agent to divide user stories according to `docs/inception/02-unit-of-work/units-plan.md`
5. User stories after work division are output to `docs/inception/02-unit-of-work/result`

## ■ Step 3. Domain Model Design (`03-domain-model-planning.md`)

**Role**: Software Engineer
**Purpose**: Design domain models to implement user stories

1. Select the user story to be the target of domain model design (e.g., `unit1-task-creation.md`) and specify it as input in `03-domain-model-planning.md`
2. Execute the prompt in `03-domain-model-planning.md`
3. A work plan document for domain model design from user stories is created: `docs/construction/03-domain-model/domain-model-plan.md`
4. Answer and save the questions listed in `docs/construction/03-domain-model/domain-model-plan.md`
5. Instruct the AI agent to divide user stories according to `docs/construction/03-domain-model/domain-model-plan.md`
6. Domain model design documents are created in `docs/construction/03-domain-model/unitX/result`

## ■ Step 4. Implementation (`04-domain-to-code-planning.md`)

**Role**: Software Engineer
**Purpose**: Implement source code from domain model design

1. Select the domain model design to be implemented (e.g., `docs/inception/03-domain-model/unitX/result/`) and specify it as input in `04-domain-to-code-planning.md`
2. Execute the prompt in `04-domain-to-code-planning.md`
3. A work plan document for implementation from domain model design is created: `docs/construction/04-domain-to-code/unitX/domain-to-code-plan.md`
4. Answer and save the questions listed in `docs/construction/04-domain-to-code/unitX/domain-to-code-plan.md`
5. Instruct the AI agent to divide user stories according to `docs/construction/04-domain-to-code/unitX/domain-to-code-plan.md`
6. Implementations are created from domain model design (e.g., `task_management`)

## ■ Step 5. Architecture Component Creation (`05-architecture-component-planning.md`)

**Role**: Software Architect
**Purpose**: Add architecture components to operate the implementations

1. Select the target implementation directory (e.g., `task_management`) and specify it as input in `05-architecture-component-planning.md`
2. Select the target divided user story (e.g., `docs/inception/02-unit-of-work/result/unitX-XXX.md`) and specify it as input in `05-architecture-component-planning.md`
3. Execute the prompt in `05-architecture-component-planning.md`
4. A work plan document for architecture component creation is created: `docs/construction/05-architecture-component/architecture-component-plan.md`
5. Answer and save the questions listed in `docs/construction/05-architecture-component/architecture-component-plan.md`
6. Instruct the AI agent to create architecture components according to `docs/construction/05-architecture-component/architecture-component-plan.md`
7. Architecture components are created

# 3. Deliverable Structure

By executing the prompts, documents and implementations are generated in the following structure:

```
docs/
├── inception/                  # Planning and design phase
│   ├── 01-user-story/
│   │   ├── user-story-plan.md
│   │   └── result/
│   └── 02-unit-of-work/
│       ├── units-plan.md
│       └── result/
│           ├── unit1-*.md
│           └── unit2-*.md
└── construction/               # Construction phase
│   ├── 03-domain-model/
│   │   └── unitX/
│   │       ├── domain-model-plan.md
│   │       └── result/
│   ├── 04-domain-to-code/
│   │   └── unitX/
│   │       └── domain-to-code-plan.md
│   └── 05-architecture-component/
│       └── architecture-component-plan.md
│
└── Source Code + Architecture Components
```

---

# AI 駆動開発ライフサイクル（AI-DLC）プロンプト

このリポジトリは、Amazon Web Services が提案する「[AI-Driven Development Lifecycle（AI-DLC）](https://prod.d13rzhkk8cj2z0.amplifyapp.com/)」のプロセスに沿ったプロダクト開発をするためのプロンプトを格納しています。

- https://aws.amazon.com/jp/blogs/news/ai-driven-development-life-cycle/

※プロンプト実行は、**Amazon Q developer CLI／Claude Code／Codex CLI などの AI エージェントの対話を前提**として設計されています。

# １．概要

本プロンプト集は、以下の 5 つのフェーズで構成されています

1. **ユーザーストーリー計画** - 要件をユーザーストーリーとして定義します
2. **作業単位分割計画** - ユーザーストーリーを実装可能な作業ユニットに分割します
3. **ドメインモデル設計計画** - ビジネスロジックのドメインモデルを設計します
4. **コード実装計画** - ドメインモデルからソースコードを実装します
5. **アーキテクチャコンポーネント計画** - 実装物を動作させるためのアーキテクチャを構築します

## ■ プロンプト構成

```
├── 01-user-story-planning.md          # ユーザーストーリー作成プロンプト
├── 02-unit-of-work-planning.md       # 作業単位分割プロンプト
├── 03-domain-model-planning.md        # ドメインモデル設計プロンプト
├── 04-domain-to-code-planning.md      # コード実装プロンプト
└── 05-architecture-component-planning.md  # アーキテクチャコンポーネント作成プロンプト

```

# ２．使用方法

## ■ 基本的な作業の流れ

1. **プロンプトを選択**: 開発フェーズに応じたプロンプトファイルを選択
2. **AI アシスタントに入力**: 選択したプロンプトを AI アシスタントに入力
3. **計画書の作成**: AI が作業計画書を作成
4. **質問への回答**: 計画書内の質問に回答
5. **計画の承認**: 作業計画をレビューし承認
6. **ステップバイステップ実行**: AI が計画に沿って 1 ステップずつ実行

## ■ ステップ 2：ユーザーストーリー作成 (`01-user-story-planning.md`)

**役割**: プロダクトオーナー
**目的**: 開発対象のシステムに対する明確なユーザーストーリーを作成

1. `01-user-story-planning.md`に作成したいものを記述し、ファイル内のプロンプトを実行します
2. ユーザストーリ作成のための作業計画書が作成されます: `docs/inception/01-user-story/user-story-plan.md`
3. `docs/inception/01-user-story/user-story-plan.md`内に質問事項が記載されているので回答し保存します
4. AI エージェントに`docs/inception/01-user-story/user-story-plan.md`に従いユーザストーリを作成するように指示します
5. `docs/inception/01-user-story/result`にユーザストーリに関するワークダウンファイルが作成されます

## ■ ステップ 2. 作業単位分割 (`02-unit-of-work-planning.md`)

**役割**: ソフトウェアアーキテクト
**目的**: ユーザーストーリーを並行実装可能な作業ユニットに分割

1. `02-unit-of-work-planning.md`内のプロンプトを実行します
2. ユーザストーリを分割するための作業計画書が作成されます: `docs/inception/02-unit-of-work/units-plan.md`
3. `docs/inception/02-unit-of-work/units-plan.md`内に質問事項が記載されているので回答し保存します
4. AI エージェントに`docs/inception/02-unit-of-work/units-plan.md`に従いユーザストーリを作業分割するように指示します
5. `docs/inception/02-unit-of-work/result`に作業分割後のユーザストーリが出力されます

## ■ ステップ 3. ドメインモデル設計 (`03-domain-model-planning.md`)

**役割**: ソフトウェアエンジニア
**目的**: ユーザーストーリーを実装するためのドメインモデル設計

1. ドメインモデル設計対象となるユーザストーリ（例：`unit1-task-creation.md`）を選択し、`03-domain-model-planning.md`のインプットに指定します
2. `03-domain-model-planning.md`内のプロンプトを実行します
3. ユーザストーリからドメインモデル設計を行うための作業計画書が作成されます: `docs/construction/03-domain-model/domain-model-plan.md`
4. `docs/construction/03-domain-model/domain-model-plan.md`内に質問事項が記載されているので回答し保存します
5. AI エージェントに`docs/construction/03-domain-model/domain-model-plan.md`に従いユーザストーリを作業分割するように指示します
6. `docs/construction/03-domain-model/unitX/result`にドメインモデル設計書が作成されます

## ■ ステップ 4. 実装 (`04-domain-to-code-planning.md`)

**役割**: ソフトウェアエンジニア
**目的**: ドメインモデル設計からソースコードを実装

1. 実装対象となるドメインモデル設計（例：`docs/inception/03-domain-model/unitX/result/`）を選択し、`04-domain-to-code-planning.md` のインプットに指定します
2. `04-domain-to-code-planning.md` 内のプロンプトを実行します
3. ドメインモデル設計から実装を行うための作業計画書が作成されます: `docs/construction/04-domain-to-code/unitX/domain-to-code-plan.md`
4. `docs/construction/04-domain-to-code/unitX/domain-to-code-plan.md` 内に質問事項が記載されているので回答し保存します
5. AI エージェントに`docs/construction/04-domain-to-code/unitX/domain-to-code-plan.md`に従いユーザストーリを作業分割するように指示します
6. ドメインモデル設計から実装物が作成されます（例：`task_management`）

## ■ ステップ 5. アーキテクチャコンポーネント作成 (`05-architecture-component-planning.md`)

**役割**: ソフトウェアアーキテクト
**目的**: 実装物を動作させるためのアーキテクチャコンポーネントを追加

1. 対象となる実装物のディレクトリ（例：`task_management`）を選択し、`05-architecture-component-planning.md` のインプットに指定します
2. 対象となる作業分割後のユーザストーリ（例：`docs/inception/02-unit-of-work/result/unitX-XXX.md`）を選択し、`05-architecture-component-planning.md` のインプットに指定します
3. `05-architecture-component-planning.md` 内のプロンプトを実行します
4. アーキテクチャコンポーネント作成のための作業計画書が作成されます: `docs/construction/05-architecture-component/architecture-component-plan.md`
5. `docs/construction/05-architecture-component/architecture-component-plan.md` 内に質問事項が記載されているので回答し保存します
6. AI エージェントに `docs/construction/05-architecture-component/architecture-component-plan.md`に従いアーキテクチャコンポーネントを作成するように指示します
7. アーキテクチャコンポーネントが作成されます

# ３．成果物の構造

プロンプト実行により、以下のような構造でドキュメントと実装物が生成されます：

```
docs/
├── inception/                  # 企画・計画フェーズ
│   ├── 01-user-story/
│   │   ├── user-story-plan.md
│   │   └── result/
│   └── 02-unit-of-work/
│       ├── units-plan.md
│       └── result/
│           ├── unit1-*.md
│           └── unit2-*.md
└── construction/               # 構築フェーズ
│   ├── 03-domain-model/
│   │   └── unitX/
│   │       ├── domain-model-plan.md
│   │       └── result/
│   ├── 04-domain-to-code/
│   │   └── unitX/
│   │       └── domain-to-code-plan.md
│   └── 05-architecture-component/
│       └── architecture-component-plan.md
│
└── ソースコード＋アーキテクチャコンポーネント
```
