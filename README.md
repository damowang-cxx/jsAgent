# HAR Agent

HAR Agent 是一个本地优先的 HAR 离线分析器。一期版本已经升级为基于 LangGraph 的节点化编排架构，但核心判断仍然完全由本地确定性规则和现有 Python 分析器完成，不依赖 Codex、OpenAI API 或任何远程模型。

输入是 HAR 文件，输出是：

- 机器可消费的 `result.json`
- 人类可读的 `report.md`

## 一期能力范围

- HAR 读取与标准化解析
- HAR 健康检查
- 目标请求筛选
- Cookie 溯源
- 字段/参数来源分析
- 值推断与轻量生成逻辑候选分析
- 自动发现 Cookie 与可疑字段
- JSON / Markdown 输出
- 自然语言目标输入
- LangGraph 本地状态图编排

## 明确不支持的内容

- 浏览器实时抓包
- CDP / DevTools Protocol
- 代理抓包
- DevTools 扩展
- 完整 JavaScript 逆向
- 云端服务
- 在 HAR 没有直接证据时声称“确定由某段 JS 生成”

## 当前架构

当前版本的主流程已经从线性 pipeline 升级为 LangGraph 编排。

图结构固定为：

```text
START
-> load_har
-> normalize_har
-> health_check
-> parse_goal
-> route_by_intent

cookie_path:
-> resolve_cookie_target
-> resolve_request_target
-> match_requests
-> run_cookie_analysis
-> review_cookie_evidence
-> finalize

field_path:
-> resolve_field_target
-> resolve_request_target
-> match_requests
-> run_field_analysis
-> review_field_evidence
-> finalize

fallback_path:
-> auto_discovery
-> finalize

END
```

### 决策层原则

- 决策层是本地确定性逻辑
- 路由只依赖规则解析结果、HAR 结构化结果、gap/confidence 规则
- 不把 Codex / LLM 放进决策层
- 不调用任何远程 API

### 预留但默认关闭的 hook

当前版本只预留接口，不启用模型调用：

- `semantic_goal_refiner`
- `analysis_explainer`
- `generation_logic_reasoner`

默认全部是 no-op，不会影响现有结果。

## 三种输入模式

### 1. `goal_prompt`

用户提供 HAR，再给一句自然语言目标，例如：

```bash
python -m har_agent.cli analyze \
  --input www.fuzhou-air.cn.har \
  --goal "分析 https://www.fuzhou-air.cn/psg-community-user/api/message/sms/sendphoneCode 接口的 \"desc\" 字段生成逻辑"
```

系统会先做本地目标解析，再把结果转成内部结构化规则。

### 2. `structured_config`

用户提供 HAR 和 YAML 配置，适合批处理或明确规则场景。

### 3. `auto_discovery`

没有 goal，也没有结构化目标时，系统会走自动发现路径，对全 HAR 做保守分析。

## 为什么当前版本不把模型放进决策层

- 目标解析和路由必须可测试、可重复、可解释
- 决策层一旦依赖模型，路由稳定性和回归测试都会变差
- 一期核心目标是“本地优先、结构化、可验证”
- 模型更适合放在后期说明层，而不是证据判断层

未来如果要接模型，建议只接在后处理阶段，例如：

- 更自然的结论归纳
- 报告润色
- 更复杂但仍显式标注为候选的生成逻辑解释

## 安装

推荐 Python 3.11+。

```bash
python -m pip install -e .[dev]
```

如需可选加速：

```bash
python -m pip install -e .[dev,speedups]
```

Windows 如果看到类似提示：

```text
har-agent.exe is installed in ...\Python\Python313\Scripts which is not on PATH
```

说明安装成功，但脚本目录没有加入 `PATH`。可以直接这样运行：

```bash
python -m har_agent.cli analyze --input sample.har --goal "分析 ..."
```

或者把下面目录加入用户 `PATH` 后重新打开终端：

```text
D:\MyConfiguration\xiangli.zhou.TCENT\AppData\Roaming\Python\Python313\Scripts
```

## CLI 用法

### 推荐用法：自然语言目标

```bash
har-agent analyze --input sample.har --goal "分析 https://example.com/api/login 接口的 \"token\" 字段生成逻辑"
```

也可以从文本文件读取目标：

```bash
har-agent analyze --input sample.har --goal-file goal.txt
```

### 结构化规则模式

```bash
har-agent analyze \
  --input sample.har \
  --config rules.yaml \
  --output-json out/result.json \
  --output-report out/report.md
```

### 自动发现模式

```bash
har-agent analyze --input sample.har
```

### 说明

- `--goal` / `--goal-file` 与 `--config` 互斥
- 默认输出到 `./out/result.json` 和 `./out/report.md`
- 旧 CLI 入口保持兼容，内部已切到 LangGraph 编排

## Cookie 路径与 Field 路径

### Cookie 路径

适用于：

- `cookie_set_source`
- `cookie_generation_logic`

路径会优先解析 Cookie 名，再解析请求目标，再做请求匹配，最后运行现有 `analyze_cookie_lineage`。

### Field 路径

适用于：

- `field_origin`
- `field_generation_logic`

路径会优先解析字段名和 scope，再解析请求目标并匹配请求，最后运行现有 `analyze_field_lineage`。

### Fallback

当目标不充分、字段/Cookie 名缺失、或 goal 模式下目标请求匹配不到时，会进入 `fallback_path`。

Fallback 行为：

- 不伪装成精准命中
- 使用自动发现逻辑分析全 HAR
- 输出 `discovered_candidate` 结果
- 保留原始 `analysis_intent` 与相关 gaps

## 配置文件示例

```yaml
target_requests:
  - name: target_api
    url_regex: "/api/"
    methods: ["GET", "POST"]
    host_contains: "example.com"

target_cookies:
  - sid
  - abck

target_fields:
  - name: request_token
    scope: request.json
    selector: "$.payload.token"

  - name: trace_id
    scope: request.header
    selector: "x-trace-id"

  - name: response_session
    scope: response.json
    selector: "$.data.session"

report:
  include_timeline: true
  include_raw_examples: true
```

## 输出 JSON 示例

```json
{
  "summary": {
    "schema_version": "1.0",
    "generated_at": "2026-03-31T02:00:00+00:00",
    "input_file": "sample.har",
    "entry_count": 42,
    "matched_request_count": 1,
    "cookie_lineage_count": 1,
    "field_analysis_count": 1,
    "gap_count": 3
  },
  "analysis_intent": {
    "input_mode": "goal_prompt",
    "analysis_kind": "field_generation_logic",
    "resolution_confidence": "high"
  },
  "health": {},
  "targets": {},
  "matched_requests": [],
  "cookie_lineage": [],
  "field_analysis": [],
  "claims": [],
  "gaps": [],
  "recommendations": []
}
```

## 报告示例片段

```md
# 用户目标

- 输入模式：`goal_prompt`
- 分析类型：`field_generation_logic`
- 原始提示词：`分析 https://example.com/api/login 接口的 "token" 字段生成逻辑`

# 目标解析结果

## 请求目标

- 原始 URL：`https://example.com/api/login`
- 匹配请求数：`1`

## 字段目标

- 字段名：`token`
- resolved scopes：`request.json`
```

## 如何理解 confidence

- `high`：HAR 内存在直接且闭环的证据
- `medium`：有较强线索，但仍存在值差异、覆盖、domain/path 不确定或多候选来源
- `low`：只有弱线索，不能形成直接闭环
- `unresolved`：HAR 中证据不足，只能保留未决结论

## 如何理解 gaps

`gaps` 用于显式表达证据缺口，而不是把不确定性藏在模糊措辞里。

当前版本至少会输出这些 gap code：

- `missing_prior_requests_before_har_start`
- `likely_sanitized_har`
- `missing_cookie_headers`
- `missing_set_cookie_headers`
- `missing_request_bodies`
- `multiple_same_name_cookie_candidates`
- `cannot_confirm_js_generation_from_har_alone`
- `incomplete_timeline`
- `parse_error_body`
- `parse_error_cookie`
- `goal_missing_request_target`
- `goal_no_matching_request`
- `goal_missing_field_name`
- `goal_missing_cookie_name`
- `goal_ambiguous_field_scope`
- `goal_no_matching_field`

## 为什么缺少敏感头会限制 Cookie 溯源

Cookie 溯源的一期目标是优先确认“设置源”。

如果 HAR 缺少以下信息：

- 请求头里的 `Cookie`
- 响应头里的 `Set-Cookie`
- 关键请求体
- HAR 开始前的前序请求

那系统最多只能确认“这个值在 HAR 中第一次何时出现”，不能把“出现”误写成“确定由某段 JS 或某个接口生成”。因此结果会明确输出：

- 低置信或未决结论
- 候选来源推断
- 显式 gaps

## 测试

```bash
pytest
```

## 后续扩展点

- 在后期分析阶段启用可选 hook
- 增加更细粒度的字段相关性规则
- 增加更强的请求聚类和时间线可视化
- 在保持本地优先的前提下，为报告层接入可选模型摘要
