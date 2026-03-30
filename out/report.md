# 执行摘要

- 输入文件：`www.fuzhou-air.cn.har`
- 总请求数：`92`
- 命中目标请求数：`0`
- Cookie 结论数：`0`
- 字段分析数：`1`
- Gap 总数：`5`

# 用户目标

- 输入模式：`goal_prompt`
- 分析类型：`field_generation_logic`
- 解析置信度：`low`
- 原始提示词：`分析 https://www.fuzhou-air.cn/psg-community-user/api/message/sms/sendphoneCode 接口的 "desc" 字段生成逻辑`

# 目标解析结果

## 请求目标

- 原始 URL：`https://www.fuzhou-air.cn/psg-community-user/api/message/sms/sendphoneCode`
- host_contains：`www.fuzhou-air.cn`
- path_contains：`/psg-community-user/api/message/sms/sendphoneCode`
- 匹配请求数：`0`

## 字段目标

- 字段名：`desc`
- scope hint：``
- resolved scopes：`request.json`
- candidate scopes：`request.json`


解析说明：
- Full URL extracted from goal prompt.
- Field scope was inferred uniquely from HAR entries matched to the target request.

解析阶段 gaps：
- `goal_no_matching_request`: Goal request target did not match any request in the HAR.

# HAR 健康检查

- `likely_sanitized`: `True`
- `missing_cookie_headers`: `True`
- `missing_set_cookie_headers`: `True`
- `missing_request_bodies`: `True`
- `incomplete_timeline`: `False`

| Gap Code | Severity | Message |
| --- | --- | --- |
| `missing_cookie_headers` | `medium` | No request cookies were present in the HAR |
| `missing_set_cookie_headers` | `medium` | No response Set-Cookie values were present in the HAR |
| `likely_sanitized_har` | `medium` | HAR appears sanitized because both request cookies and response Set-Cookie values are absent |
| `missing_request_bodies` | `low` | 1 state-changing requests did not contain request bodies |

# 目标请求概览

未命中显式目标请求；当前结果保留自动分析结果。

# Cookie 溯源

未发现 Cookie。

# 字段分析

## `desc` (`request.json` / `$..desc`)

- discovered_candidate：`False`
- 首次出现：`request.json@entry-0070`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |

编码识别：
- `urlencoded`: URL decoding changed the original value.

结构识别：
- `random_like`: Value length and entropy suggest a random-looking token.

| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |

值样例：
```json
[
  "FJYtbr5DeAP9zP1J6RSOwnZx35fUrXLW2j2ZtexcK%2BgQ9U24eeJVwfp2a6A0mqh%2Bam8ao9LSfPKpMqERXlL7%2B%2BtY9VY787kmxX/cK8A1p7bqkJVBqT3Mukbql7mX3gJ8goFn9mFUYKautN2oMP83mfYd0Gv5UReeVd6tUokOV7xcwUg5MbwqYKVzyK1obAj0fbAkkZGzDgnULkMkYXG/LyxiJDc90Rxz3U6TMPwm4aPuvbywh6wg3vGPOcCJ3vWKja0K2dYYce6DKKLRszIfRE9vk6cHGi0Ad03ns59B7gyetYbymd1ndqfSq4Z2VdbrRPILXMMYhJ5QK71g98Tqv8oFhCsaSHNO9nEkhkRh0YBmFALxjUhQ6ynp2HftSzV4a/Ys3kwWknGvtYhlKdPTJaEohkROAhfrAAaQVb2Svq1AnhwO1C2uXpSxNAvGUO6cwBVesxETFXuFUFt5iMGe8vg18OhskbdncvdMnz9Z09tlrtlFTlbsHTHUYm15HnZbBHk6eLcmXe1FsS/3TdiV0sER2Epw6%2BXE//PYpOBrIUo7eOcvQq5%2B4Az4HNk3n5ea"
]
```


# 主要 Claims

- `inferred_candidate` / `medium`: 字段 desc 分析 - desc 首次出现在 request.json@entry-0070

# Gaps 与证据不足说明

- `missing_cookie_headers`: No request cookies were present in the HAR
- `missing_set_cookie_headers`: No response Set-Cookie values were present in the HAR
- `likely_sanitized_har`: HAR appears sanitized because both request cookies and response Set-Cookie values are absent
- `missing_request_bodies`: 1 state-changing requests did not contain request bodies
- `goal_no_matching_request`: Goal request target did not match any request in the HAR.

# 下一步建议

- Capture a HAR that retains Cookie headers if cookie lineage is a priority.
- Capture a HAR that retains Set-Cookie headers to confirm cookie setting sources.
- The HAR looks sanitized. Re-export it with request cookies, Set-Cookie headers, and full request bodies preserved.
- Re-record requests with request bodies preserved to improve field lineage and generation-candidate analysis.
