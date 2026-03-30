# HAR Agent

HAR Agent 是一个本地优先的 HAR 离线分析器。一期版本只接受 HAR 文件输入，通过纯 Python 的结构化分析输出：

- 机器可消费的 `result.json`
- 人类可读的 `report.md`

项目重点是稳定、可测试、可扩展，而不是“看起来聪明但不可验证”的结论。所有主要结论都必须显式附带 `confidence` 和 `gaps`，并区分：

- `direct_evidence`
- `inferred_candidate`
- `unresolved`

## 一期能力范围

- HAR 读取与标准化解析
- 目标请求筛选
- Cookie 溯源
- 任意字段分析
- 值推断与轻量候选生成逻辑
- HAR 健康检查
- 自动发现 Cookie 和可疑字段候选
- JSON/Markdown 输出
- 本地 CLI 运行

## 明确不支持的内容

- 浏览器实时抓包
- CDP / DevTools Protocol
- 代理抓包
- DevTools 扩展
- 完整 JavaScript 逆向
- 云端服务
- 声称“确定是某段 JS 生成了某个 Cookie/字段”但 HAR 内没有直接证据的结论

## 安装

推荐 Python 3.11+。

```bash
python -m pip install -e .[dev]
```

如果你希望启用更快的 JSON 序列化：

```bash
python -m pip install -e .[dev,speedups]
```

## CLI 用法

最小用法：

```bash
har-agent analyze --input sample.har
```

带配置和显式输出路径：

```bash
har-agent analyze \
  --input sample.har \
  --config rules.yaml \
  --output-json out/result.json \
  --output-report out/report.md
```

帮助信息：

```bash
har-agent --help
har-agent analyze --help
```

默认输出文件：

- `./out/result.json`
- `./out/report.md`

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
    "generated_at": "2026-03-30T07:23:31.891634+00:00",
    "input_file": "sample.har",
    "entry_count": 42,
    "matched_request_count": 3,
    "cookie_lineage_count": 2,
    "field_analysis_count": 5,
    "gap_count": 4
  },
  "health": {
    "likely_sanitized": false,
    "missing_cookie_headers": false,
    "missing_set_cookie_headers": false,
    "missing_request_bodies": true,
    "incomplete_timeline": false
  },
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
# 执行摘要

- 输入文件：`sample.har`
- 总请求数：`42`
- 命中目标请求数：`3`

# Cookie 溯源

## `sid`

- 首次出现：`response.set-cookie@entry-0007`
- confidence：`high`

| Candidate Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `response.set-cookie` | `entry-0007` | `high` | A prior Set-Cookie had the same name and exact value before the cookie was sent later. |
```

## 如何理解 confidence

- `high`：HAR 内存在直接且闭环的证据，例如前序 `Set-Cookie` 与后续 `Cookie` 同名同值。
- `medium`：有较强线索，但仍存在值差异、覆盖、domain/path 不确定或多个候选源。
- `low`：只有弱线索，不能形成直接闭环。
- `unresolved`：HAR 中没有足够证据确认来源，只能保留未决结论。

## 如何理解 gaps

`gaps` 用于明确说明证据缺口，而不是把缺口隐藏在模糊措辞里。一期至少会输出这些 gap code：

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

## 为什么缺少敏感头会限制 Cookie 溯源

Cookie 溯源的首要目标是找“设置源”。如果 HAR 里缺少：

- 请求侧 `Cookie`
- 响应侧 `Set-Cookie`
- 关键请求体
- HAR 开始前的前序请求

那么工具只能判断“值第一次在 HAR 中何时出现”，而不能把“出现”误写成“确定由某个地方生成”。这也是为什么一期结果会在证据不足时输出：

- 低置信或未决结论
- 候选来源推断
- 显式 `gaps`

而不会声称“就是某段 JS 生成的”。

## 本地运行示例

```bash
python -m har_agent.cli analyze --input tests/fixtures/basic.har
```

## 测试

```bash
pytest
```

## 后续扩展点

- 在 `analysis.pipeline` 之上增加本地 API 层
- 引入更细粒度的字段相关性规则
- 增加更强的请求聚类与时间线可视化
- 在保留本地优先前提下增加可选模型摘要层
