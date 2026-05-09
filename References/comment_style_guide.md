# MUC-QMJH 注释规范

本规范统一脚本的注释风格，供后续开发和 Copilot 辅助时参照。

---

## 规则 1：文件头部文档字符串

每个脚本文件的第一行必须是三引号文档字符串，格式固定为四段：

```python
"""
C00_script_name                          ← 文件名（不含扩展名）

一句话功能说明。                           ← 不超过 35 字，动宾结构

功能：
- 操作 A（一句话描述）
- 操作 B
- 操作 C

数据流向：
  输入文件（行数 × 列数）→ 核心操作描述 → 输出文件（行数 × 列数）
  + 附加输出文件（可选）
"""
```

**要求：**
- 文件名段与说明段之间空一行
- 功能段每条以 `- ` 开头，动词起头，简洁
- 数据流向使用 `→` 符号，标注关键数量
- 例如 C14/C15 等可视化脚本数据流向末尾加 `→ 可视化图像输出`

---

## 规则 2：相同函数的注释完全一致

跨文件出现的相同或功能等价函数，其 docstring 和行内注释必须**逐字相同**。

**路径工厂函数标准模板**（出现在所有文件）：

```python
def get_xxx_path(root: Path | str | None = None) -> Path:
    """返回 XXX parquet 文件的默认路径。"""

    # 支持传入自定义根目录，便于测试或在不同目录下运行脚本
    if root is None:
        root_path : Path = Path.cwd()
    else:
        root_path : Path = Path(root)

    # XXX 文件位于项目根目录下的 Data/xxx/xxx.parquet
    return root_path / "Data" / "xxx" / "xxx.parquet"
```

**路径分支注释**（出现在 touch/analyze 类主函数中）：

```python
# 支持传入自定义文件路径，便于测试或在不同目录下运行脚本
if file_path is None:
    file_path : Path = get_xxx_path()
else:
    file_path : Path = Path(file_path)

# 默认输出目录为当前工作目录下的 Reports （或其他文件夹）
if output_dir is None:
    output_dir : Path = Path.cwd() / "Reports"
else:
    output_dir : Path = Path(output_dir)

# 提前创建输出目录，避免后续保存时因目录不存在而失败
output_dir.mkdir(parents=True, exist_ok=True)
```

---

## 规则 3：内部运行逻辑分层标注

函数体内的注释使用数字编号进行分层，层级关系如下：

| 层级 | 格式 | 用途 |
|------|------|------|
| 顶层步骤 | `# 1. 描述` | 函数内的主要阶段，通常 3–6 个 |
| 子步骤 | `# 1.1 描述` | 顶层步骤内的细分操作 |
| 细节说明 | `# 1.1.1 描述` | 特殊逻辑、边界条件，谨慎使用 |

**示例：**

```python
def process_data(df):
    # 1. 过滤无效记录
    df = df[df["evaluation_order"] == 1]

    # 2. 提取对话特征
    # 2.1 提取用户输入 token 数
    user_tokens = df["sum_user_tokens"]
    # 2.2 提取模型 A/B 响应 token 数
    a_tokens = df["a_assistant_tokens"]
    b_tokens = df["b_assistant_tokens"]

    # 3. 计算长度比率
    df["length_ratio"] = a_tokens / user_tokens.clip(lower=1)

    return df
```

**注意：**
- 编号注释单独占一行，不写在代码行末尾
- 同一函数内编号连续，不跨函数重置
- 少于 3 步的简单函数无需编号

---

## 规则 4：禁止使用分隔线，改用空行分层

在注释中禁止使用 `# ===...===`、`# ---...---` 等横线式分隔符。

代码块之间的分隔通过**空行**实现：
- 顶层函数之间：2 个空行（PEP 8 标准）
- 函数内逻辑段落之间：1 个空行
- 函数内紧邻的同组语句之间：无空行

**禁止：**
```python
# ========================================================================
# 路径管理函数
# ========================================================================
```

**允许：**
```python
# 路径管理函数

def get_xxx_path(...):
```

---

## 规则 5：中英文混排间距

中文文本与英文字母/数字/标识符之间留一个半角空格。

| 错误 | 正确 |
|------|------|
| `parquet文件` | `parquet 文件` |
| `token数` | `token 数` |
| `DataFrame格式` | `DataFrame 格式` |
| `evaluation_order字段` | `evaluation_order 字段` |
| `135634行` | `135,634 行` |

---

## 规则 6：行内注释规范

行内注释（代码行末尾的 `#`）遵循以下限制：

- 与代码末尾至少间隔 **2 个空格**
- 内容不超过 **40 个字符**（含空格）
- 超过限制时，改为代码行**上方**的独立注释行

**示例：**
```python
# 正确显示负号（matplotlib 默认会将负号显示为方框）
plt.rcParams['axes.unicode_minus'] = False
```

---

## 规则 7：禁止冗余注释

不注释代码本身已清晰表达的内容；只注释"为什么"或非直觉的业务逻辑。

**禁止：**
```python
i += 1  # i 加 1
df.dropna()  # 删除空值
output_dir.mkdir(parents=True, exist_ok=True)  # 创建目录
```

**允许：**
```python
df = df[df["evaluation_order"] == 1]
# evaluation_order > 1 的记录含有会话历史 token，会高估用户输入长度，须过滤
```

---

## 规则 8：多行 docstring 结构固定顺序

所有多行 docstring 遵循以下固定结构（缺少的节可省略，但顺序不变）：

```python
def func(param: Type) -> Type:
    """
    一句话摘要（动宾结构，不超过 35 字）。

    补充说明段落（可选，用于解释函数的使用背景或注意事项）。

    参数说明：
    - param_name：说明（含类型提示和默认值说明）

    返回值：
    - 返回内容说明
    """
```

**要求：**
- 第一行是摘要，不加空行直接在 `"""` 后另起一行
- 摘要与参数说明之间空一行
- 参数说明节标题为 `参数说明：`，返回值节标题为 `返回值：`
- 单行 docstring 写在同一行：`"""返回 XXX 路径。"""`

---

## 快速对照表

| 维度 | 规则 | 典型改法 |
|------|------|---------|
| 文件头 | R1 | 文件名 + 说明 + 功能 + 数据流向 |
| 跨文件一致 | R2 | 路径函数用标准模板 |
| 内部逻辑 | R3 | 改为 `# 1.` / `# 1.1` 编号 |
| 分隔线 | R4 | 删除 `===` / `---`，改用空行 |
| 中英混排 | R5 | `token数` → `token 数` |
| 行内注释 | R6 | 超 40 字移到代码上方 |
| 冗余注释 | R7 | 删除重述代码的注释 |
| Docstring | R8 | 摘要 → 参数说明 → 返回值 |
