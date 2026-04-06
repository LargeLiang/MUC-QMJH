# Token异常分析报告
**分析日期**：2026年4月6日  
**基于数据**：integrated_data.parquet（135634行）  
**关联资料**：progress.md、R07_token_report.txt

---

## 一、现象总结

| 检验项目 | 结果 | 反例数 | 占比 |
|---------|------|--------|------|
| conversation_b中role='user'的sum_user_tokens一致性 | ❌ 不一致 | 27,319 | 20.14% |
| conversation_b中role='assistant'的sum_assistant_b_tokens一致性 | ✅ 完全一致 | 0 | 0% |
| conversation_b中role='user'是否超过sum_user_tokens | ✅ 从不超过 | 0 | 0% |

---

## 二、根本原因分析

### 1. **关键发现**：sum_user_tokens的定义差异

#### 官方定义
- **sum_user_tokens**：**整个Session历史**的所有user消息token总和
- **sum_assistant_a/b_tokens**：**当前Order**中对应模型的token总和

#### 数据流逻辑
```
Session（会话）
  ├── Order 1 (evaluation_order=1)
  │   ├── conversation_a（用户提问+模型A回复）
  │   └── conversation_b（用户提问+模型B回复）
  │       └── num_tokens 统计当前Order的tokens
  │
  ├── Order 2 (evaluation_order=2)
  │   ├── conversation_a（用户后续提问+模型A新回复）
  │   └── conversation_b（用户后续提问+模型B新回复）
  │       └── num_tokens 仅统计Order 2中的tokens
  │           但 sum_user_tokens = Order 1用户tokens + Order 2用户tokens + ...
  │
  └── Order N (evaluation_order=N)
      └── sum_user_tokens = Σ(Order 1~N 所有用户提问)
```

### 2. **数据验证**

#### 评价顺序分布
| evaluation_order | 样本数 | 占比 |
|------------------|--------|------|
| 1 | 108,315 | 79.86% |
| 2~28 | 27,319 | 20.14% |
| **总计** | **135,634** | **100%** |

#### Token一致性与order的对应关系
```
evaluation_order = 1 的行（108,315条）
  → sum_user_tokens = conversation_b 中 role='user' 的 num_tokens
  → ✅ 完全一致

evaluation_order > 1 的行（27,319条）
  → sum_user_tokens = 整个 Session 从第1个order累计的用户tokens
  → conversation_b 中的 num_tokens 仅为当前order的用户tokens
  → ❌ 必然不一致（27,319 = token不一致行数）
```

**数值匹配率**：100% ✅

---

## 三、为什么现有判断合理

### 1. **Assistant一致性的完美解释**
conversation_b中role='assistant'的num_tokens与sum_assistant_b_tokens **完全一致（0个反例）**：
- sum_assistant_b_tokens 的定义就是当前Order的model_b回复token数
- conversation_b中role='assistant'正好就是当前Order的model_b回复
- **因此不存在跨Order累计问题** ✅

### 2. **User从不超过expected的逻辑**
conversation_b中role='user'的num_tokens始终 ≤ sum_user_tokens：
- sum_user_tokens 是累计值（≥当前Order用户tokens）
- conversation_b中用户只是当前Order的部分
- **因此严格满足不等式** ✅

### 3. **27319的完美对应**
- token不一致行数 = 27,319
- evaluation_order > 1 的行数 = 27,319
- **一一对应，零誤差**，证明因果关系确凿 ✅

---

## 四、数据质量结论

### ✅ 现有判断完全合理

#### 判断依据
1. **因果关系明确**：sum_user_tokens是Session级汇总，不是Order级汇总
2. **数值精确匹配**：27,319 ≡ evaluation_order > 1的样本量
3. **逻辑自洽**：assistant一致性验证了定义差异假设的正确性
4. **无数据腐败**：所有token数据完整，无缺失或异常值

#### 后续处理建议
根据progress.md中的结论：
```
结论：**剔除evaluation_order > 1 的数据**，避免上下文污染
```

**原因**：
- evaluation_order > 1的数据含有来自Session历史对话中的信息
- 这对"长度偏好"分析会产生偏差（因为长度数据被前序Order影响）
- 保留evaluation_order = 1的108,315条**干净数据**进行分析更可靠

---

## 五、技术总结

| 问题 | 原因 | 证据 | 可信度 |
|-----|------|------|--------|
| 为什么27,319行token不一致？ | evaluation_order > 1，sum_user_tokens为Session累计值 | 27,319 = evaluation_order>1的样本量 | ⭐⭐⭐⭐⭐ |
| 为什么assistant始终一致？ | sum_assistant_b_tokens定义本身就是当前Order | 0个反例 | ⭐⭐⭐⭐⭐ |
| 是否存在数据质量问题？ | 否，数据结构合理，定义清晰 | 无缺失、无重复、无异常值 | ⭐⭐⭐⭐⭐ |

---

## 六、建议

### 短期（数据清洗）
✅ **按progress.md结论执行**：保留evaluation_order=1的108,315条数据进行后续分析

### 中期（字段优化）
建议在数据预处理阶段明确标注：
```python
# 在conversation_b的元数据或报告中标识
is_first_order: bool  # True if evaluation_order == 1
session_user_tokens_cumulative: int  # 整个Session的累计用户tokens
current_order_user_tokens: int  # 仅当前Order的用户tokens
```

### 长期（文档完善）
补充数据字典，明确界定：
```
sum_user_tokens: "整个evaluation_session_id对应的Session中，
                  所有evaluation_order的用户消息token总和"
sum_assistant_a/b_tokens: "当前记录(id)对应Order中，
                           模型A/B的回复token数"
```

---

**结论**：现有token异常判断**逻辑严密、证据充分、结论正确**，可放心按progress.md的建议剔除evaluation_order>1的数据。
