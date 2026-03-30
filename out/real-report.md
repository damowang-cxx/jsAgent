# 执行摘要

- 输入文件：`www.fuzhou-air.cn.har`
- 总请求数：`92`
- 命中目标请求数：`20`
- Cookie 结论数：`0`
- 字段分析数：`15`
- Gap 总数：`4`

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

| Entry | Method | Status | Score | URL |
| --- | --- | --- | --- | --- |
| `entry-0085` | `POST` | `200` | `70.0` | `https://cap.dingxiang-inc.com/api/v1` |
| `entry-0086` | `POST` | `200` | `21.0` | `https://www.fuzhou-air.cn/hnatravel/verify` |
| `entry-0078` | `POST` | `200` | `14.0` | `https://constid.dingxiang-inc.com/udid/c1` |
| `entry-0000` | `GET` | `200` | `5.0` | `https://www.fuzhou-air.cn/micro/user/login` |
| `entry-0001` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/app/main/css/browser.css` |
| `entry-0002` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/_next/static/css/2eb603ecdf4d8d02.css` |
| `entry-0003` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/_next/static/chunks/webpack-29e5e3bd47de074c.js` |
| `entry-0004` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/_next/static/chunks/framework-0ba0ddd33199226d.js` |
| `entry-0005` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/_next/static/chunks/main-195a5be1bed5ad35.js` |
| `entry-0006` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/_next/static/chunks/pages/_app-1da1264c726285d5.js` |
| `entry-0007` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/_next/static/chunks/pages/micro/%5B...page%5D-9a25c07860b2a875.js` |
| `entry-0008` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/_next/static/GoRhpFoWGcBzLYaou8J-h/_buildManifest.js` |
| `entry-0009` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/_next/static/GoRhpFoWGcBzLYaou8J-h/_ssgManifest.js` |
| `entry-0010` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/fecms.pub.bucket.fu/20250424/_a1cef53074be420f9942ff8d263a29ce.jpg` |
| `entry-0011` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/_next/static/media/symbol.0c80a8e9.png` |
| `entry-0012` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/app/main/js/browser.js` |
| `entry-0013` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/hnatravel/js/born.min.js` |
| `entry-0014` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/app/main/js/security.js` |
| `entry-0015` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/app/main/js/webJs.js` |
| `entry-0016` | `GET` | `200` | `4.78` | `https://www.fuzhou-air.cn/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fgawb.4d0b3a50.png&w=32&q=75` |

# Cookie 溯源

未发现 Cookie。

# 字段分析

## `Param` (`request.form` / `Param`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0078`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0016:request.query:q` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0016:request.query:w` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0016:response.header:content-length` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |


结构识别：
- `random_like`: Value length and entropy suggest a random-looking token.

| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0016:request.query:q` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0016:request.query:w` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0016:response.header:content-length` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |

值样例：
```json
[
  "5528#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"
]
```

## `_t` (`request.form` / `_t`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0078`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0018:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `request_field` | `entry-0033:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `response.json` | `entry-0034:response.json:$.code` | `low` | Target value contains an earlier observed value as a substring. |



| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0033:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0034:response.json:$.code` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[0].container` | `low` | Target value shares a prefix or suffix with an earlier observed value. |

值样例：
```json
[
  "09996"
]
```

## `ac` (`request.form` / `ac`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0085`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0016:request.query:w` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |


结构识别：
- `random_like`: Value length and entropy suggest a random-looking token.

| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0016:request.query:w` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |

值样例：
```json
[
  "5598#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"
]
```

## `aid` (`request.form` / `aid`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0085`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |



| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |

值样例：
```json
[
  "dx-1774851098454-78668015-1"
]
```

## `ak` (`request.form` / `ak`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0085`
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
- `hex`: Value is an even-length hexadecimal string.

结构识别：
- `random_like`: Value length and entropy suggest a random-looking token.
- `hash_like`: Value length and alphabet match common hex hash digests.

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
  "8708ec127818f8eb96ad12afc134ebba"
]
```

## `c` (`request.form` / `c`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0085`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |


结构识别：
- `random_like`: Value length and entropy suggest a random-looking token.

| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0033:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |

值样例：
```json
[
  "69ca141c5jMdpLenM9R6blFc3H9CwF3SYKhhrJB1"
]
```

## `h` (`request.form` / `h`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0085`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |



| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0033:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |

值样例：
```json
[
  "165"
]
```

## `jsv` (`request.form` / `jsv`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0085`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |

编码识别：
- `jwt_shape`: Value matches the common three-part JWT structure.


| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0033:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |

值样例：
```json
[
  "5.1.53"
]
```

## `s_p_type` (`request.form` / `s_p_type`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0086`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0016:request.query:w` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |



| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0016:request.query:w` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |

值样例：
```json
[
  "32041"
]
```

## `sid` (`request.form` / `sid`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0085`
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
- `hex`: Value is an even-length hexadecimal string.

结构识别：
- `random_like`: Value length and entropy suggest a random-looking token.
- `hash_like`: Value length and alphabet match common hex hash digests.

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
  "bf73cf330e0a10f02fcfa471816a8cb6"
]
```

## `uid` (`request.form` / `uid`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0085`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0017:response.header:access-control-allow-origin` | `medium` | Values match after base64 decoding one side. |
| `request_field` | `entry-0018:response.header:access-control-allow-origin` | `medium` | Values match after base64 decoding one side. |
| `request_field` | `entry-0032:request.header:referer` | `medium` | Observed exact same value earlier in the HAR. |
| `request_field` | `entry-0033:request.header:referer` | `medium` | Observed exact same value earlier in the HAR. |
| `response.json` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[0].container` | `high` | Observed exact same value earlier in the HAR. |



| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `encoded_from_source` | `entry-0017:response.header:access-control-allow-origin` | `medium` | Values match after base64 decoding one side. |
| `encoded_from_source` | `entry-0018:response.header:access-control-allow-origin` | `medium` | Values match after base64 decoding one side. |
| `copied_from_request_field` | `entry-0032:request.header:referer` | `medium` | Observed exact same value earlier in the HAR. |
| `copied_from_request_field` | `entry-0033:request.header:referer` | `medium` | Observed exact same value earlier in the HAR. |
| `copied_from_response` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[0].container` | `high` | Observed exact same value earlier in the HAR. |
| `copied_from_response` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[1].container` | `high` | Observed exact same value earlier in the HAR. |

值样例：
```json
[
  ""
]
```

## `validate` (`request.form` / `validate`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0086`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.query:compress` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |


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
  "4EF1DB3A3FF1B6F938B43F9B65A09C164653120A5291D1C8765554E3B8B02B08838521F5D9FD8D86AE466CAF7238F9CD560420A8FFD5C98D7342A7E1862DE8E409220839CB701EFD892A3A02681A2438:69ca141c5jMdpLenM9R6blFc3H9CwF3SYKhhrJB1"
]
```

## `verify` (`request.form` / `verify`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0086`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `request_field` | `entry-0033:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `response.json` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[0].container` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `response.json` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[1].container` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `request_field` | `entry-0057:response.header:token` | `low` | Target value shares a prefix or suffix with an earlier observed value. |



| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0033:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[0].container` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[1].container` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0057:response.header:token` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0058:response.header:token` | `low` | Target value shares a prefix or suffix with an earlier observed value. |

值样例：
```json
[
  "dx"
]
```

## `w` (`request.form` / `w`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0085`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0018:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `request_field` | `entry-0033:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `response.json` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[0].container` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `response.json` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[1].container` | `low` | Target value shares a prefix or suffix with an earlier observed value. |



| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0018:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0033:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[0].container` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0034:response.json:$.data.modules.63db6927257effa4641ba387.list[1].container` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0057:response.header:token` | `low` | Target value shares a prefix or suffix with an earlier observed value. |

值样例：
```json
[
  "255"
]
```

## `x` (`request.form` / `x`)

- discovered_candidate：`True`
- 首次出现：`request.form@entry-0085`
- confidence：`medium`
- 相关 Cookie：``

| Source Type | Ref | Confidence | Rationale |
| --- | --- | --- | --- |
| `request_field` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `request_field` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |



| Generation Candidate | Source | Confidence | Rationale |
| --- | --- | --- | --- |
| `concatenated_from_multiple_values` | `entry-0000:request.header:upgrade-insecure-requests` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0017:request.json:$[0].globalSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0018:request.json:$[0].eventSequenceId` | `low` | Target value contains an earlier observed value as a substring. |
| `concatenated_from_multiple_values` | `entry-0032:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |
| `concatenated_from_multiple_values` | `entry-0033:request.header:referer` | `low` | Target value shares a prefix or suffix with an earlier observed value. |

值样例：
```json
[
  "171"
]
```


# 主要 Claims

- `inferred_candidate` / `medium`: 字段 Param 分析 - Param 首次出现在 request.form@entry-0078
- `inferred_candidate` / `medium`: 字段 _t 分析 - _t 首次出现在 request.form@entry-0078
- `inferred_candidate` / `medium`: 字段 ac 分析 - ac 首次出现在 request.form@entry-0085
- `inferred_candidate` / `medium`: 字段 aid 分析 - aid 首次出现在 request.form@entry-0085
- `inferred_candidate` / `medium`: 字段 ak 分析 - ak 首次出现在 request.form@entry-0085
- `inferred_candidate` / `medium`: 字段 c 分析 - c 首次出现在 request.form@entry-0085
- `inferred_candidate` / `medium`: 字段 h 分析 - h 首次出现在 request.form@entry-0085
- `inferred_candidate` / `medium`: 字段 jsv 分析 - jsv 首次出现在 request.form@entry-0085
- `inferred_candidate` / `medium`: 字段 s_p_type 分析 - s_p_type 首次出现在 request.form@entry-0086
- `inferred_candidate` / `medium`: 字段 sid 分析 - sid 首次出现在 request.form@entry-0085
- `inferred_candidate` / `medium`: 字段 uid 分析 - uid 首次出现在 request.form@entry-0085
- `inferred_candidate` / `medium`: 字段 validate 分析 - validate 首次出现在 request.form@entry-0086
- `inferred_candidate` / `medium`: 字段 verify 分析 - verify 首次出现在 request.form@entry-0086
- `inferred_candidate` / `medium`: 字段 w 分析 - w 首次出现在 request.form@entry-0085
- `inferred_candidate` / `medium`: 字段 x 分析 - x 首次出现在 request.form@entry-0085

# Gaps 与证据不足说明

- `missing_cookie_headers`: No request cookies were present in the HAR
- `missing_set_cookie_headers`: No response Set-Cookie values were present in the HAR
- `likely_sanitized_har`: HAR appears sanitized because both request cookies and response Set-Cookie values are absent
- `missing_request_bodies`: 1 state-changing requests did not contain request bodies

# 下一步建议

- Capture a HAR that retains Cookie headers if cookie lineage is a priority.
- Capture a HAR that retains Set-Cookie headers to confirm cookie setting sources.
- The HAR looks sanitized. Re-export it with request cookies, Set-Cookie headers, and full request bodies preserved.
- Re-record requests with request bodies preserved to improve field lineage and generation-candidate analysis.
