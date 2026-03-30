# HAR Agent

HAR Agent 是一个本地优先的 HAR 离线分析器。当前版本支持两种输入方式：

1. `HAR + 自然语言目标`
2. `HAR + YAML 配置`

推荐主入口是自然语言目标模式。用户先提供 HAR 文件，再提供一句分析目标，例如：

```bash
python -m har_agent.cli analyze \
  --input www.fuzhou-air.cn.har \
  --goal "分析 https://www.fuzhou-air.cn/psg-community-user/api/message/sms/sendphoneCode 接口的 \"desc\" 字段生成逻辑"
```

工具会先做本地目标解析，再基于 HAR 做结构化分析，最终输出：

- 机器可消费的 `result.json`
- 人类可读的 `report.md`

## 一期能力范围

- HAR 读取与标准化解析
- 目标请求筛选
- Cookie 溯源
- 任意字段分析
- 值推断与轻量候选生成逻辑
- HAR 健康检查
- 自动发现 Cookie 和可疑字段候选
- JSON / Markdown 输出
- 本地 CLI 运行
- 本地自然语言目标解析

## 明确不支持的内容

- 浏览器实时抓包
- CDP / DevTools Protocol
- 代理抓包
- DevTools 扩展
- 完整 JavaScript 逆向
- 云端服务
- 在 HAR 没有直接证据时声称“确定由某段 JS 生成”

## 安装

推荐 Python 3.11+：

```bash
python -m pip install -e .[dev]
```

如果需要可选的更快 JSON 序列化：

```bash
python -m pip install -e .[dev,speedups]
```

Windows 如果安装日志提示：

- `har-agent.exe is installed in ...\\Python\\Python313\\Scripts which is not on PATH`

说明包已经安装成功，但命令目录还没加入 `PATH`。此时可以直接运行：

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

也可以把目标写入文本文件：

```bash
har-agent analyze --input sample.har --goal-file goal.txt
```

### 高级用法：结构化 YAML

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

- `--goal` / `--goal-file` 和 `--config` 不能同时使用
- `--goal` 模式下会先解析目标，再生成内部结构化规则
- 默认输出文件：
  - `./out/result.json`
  - `./out/report.md`

## 自然语言目标的本地工作方式

自然语言目标模式是纯本地、确定性规则解析，不调用外部 API。

工作过程固定为：

1. 从 prompt 中提取 URL、字段名、Cookie 名、分析类型和显式 scope 提示
2. 生成 `analysis_intent`
3. 把解析结果转成内部 `TargetRequestRule` / `FieldRef` / `target_cookies`
4. 运行现有 HAR 分析 pipeline
5. 在输出中同时保留“目标解析结论”和“HAR 证据结论”

这意味着：

- Codex 插件可以作为 VSCode 里的本地交互入口
- 但仓库代码本身不嵌入 OpenAI API client
- 也不会依赖联网模型来完成核心分析

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
    "matched_request_count": 1,
    "cookie_lineage_count": 0,
    "field_analysis_count": 1,
    "gap_count": 3
  },
  "analysis_intent": {
    "input_mode": "goal_prompt",
    "original_prompt": "分析 https://example.com/api/login 接口的 \"token\" 字段生成逻辑",
    "analysis_kind": "field_generation_logic",
    "resolved_request": {
      "url": "https://example.com/api/login",
      "match_count": 1
    },
    "resolved_field": {
      "name": "token",
      "resolved_scopes": ["request.json"]
    },
    "resolution_confidence": "high",
    "resolution_gaps": [],
    "resolution_notes": ["Full URL extracted from goal prompt."]
  }
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

- `high`：HAR 内存在直接且闭环的证据，例如前序 `Set-Cookie` 与后续 `Cookie` 同名同值
- `medium`：有较强线索，但仍存在值差异、覆盖、domain/path 不确定或多个候选源
- `low`：只有弱线索，不能形成直接闭环
- `unresolved`：HAR 中没有足够证据确认来源，只能保留未决结论

## 如何理解 gaps

`gaps` 用于明确说明证据缺口，而不是把缺口隐藏在模糊措辞里。当前至少会输出这些 gap code：

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

Cookie 溯源的首要目标是找“设置源”。如果 HAR 里缺少：

- 请求侧 `Cookie`
- 响应侧 `Set-Cookie`
- 关键请求体
- HAR 开始前的前序请求

那么工具只能判断“值第一次在 HAR 中何时出现”，而不能把“出现”误写成“确定由某个地方生成”。因此在证据不足时，结果会输出：

- 低置信或未决结论
- 候选来源推断
- 显式 `gaps`

## 测试

```bash
pytest
```

## 后续扩展点

- 在 `analysis.pipeline` 之上增加本地 API 层
- 引入更细粒度的字段相关性规则
- 增加更强的请求聚类与时间线可视化
- 在保持本地优先的前提下增加可选模型摘要层
