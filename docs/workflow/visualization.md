# Visualization

## Item 24: Use workflow.executors and workflow.edge_groups, Not workflow.graph

工作流可视化时，使用正确的属性名：`.executors` 和 `.edge_groups`，不是 `.graph.nodes`。

## 错误做法

```python
# 报错：Workflow 没有 graph 属性
for node in workflow.graph.nodes:
    print(node.id)

# 报错：没有 workflow_id 属性
print(workflow.workflow_id)
```

## 正确做法

```python
# 节点遍历
for exec_id, executor in workflow.executors.items():
    print(f"{exec_id}: {type(executor).__name__}")

# 边遍历
for edge_group in workflow.edge_groups:
    for edge in edge_group.edges:
        print(f"{edge.source_id} → {edge.target_id}")

# 工作流 ID
print(workflow.id)  # 不是 workflow_id
```

## 输出格式

| 格式 | 用途 |
|------|------|
| ASCII | 终端快速查看 |
| Mermaid | 文档嵌入 |
| DOT | 专业绘图 |
| JSON | 程序化处理 |

## Mermaid 示例

```python
mermaid_lines = ["flowchart TD"]

for exec_id in workflow.executors.keys():
    mermaid_lines.append(f"    {exec_id}[{exec_id}]")

for edge_group in workflow.edge_groups:
    for edge in edge_group.edges:
        mermaid_lines.append(f"    {edge.source_id} --> {edge.target_id}")

print("\n".join(mermaid_lines))
```

## Things to Remember

- **`workflow.executors`**：dict，键是 executor id，值是 executor 实例
- **`workflow.edge_groups`**：list，包含多个 EdgeGroup
- **`workflow.id`**：工作流实例 ID（不是 workflow_id）
- **节点遍历**：`for exec_id, executor in workflow.executors.items()`
- **边遍历**：`for edge_group in workflow.edge_groups: for edge in edge_group.edges`
