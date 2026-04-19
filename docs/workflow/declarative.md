# Declarative Workflows

## Item 21: Think of Declarative as YAML-First, Not YAML-Only

Declarative Workflow 用 YAML 描述工作流结构，但解析后还是用代码执行。YAML 是声明，不是代码。

## YAML 结构

```yaml
name: text_processing_workflow
version: "1.0"

executors:
  upper_case:
    type: class
    class: UpperCase
    config:
      id: upper_case

  reverse:
    type: function
    function: reverse
    config:
      id: reverse

edges:
  - from: upper_case
    to: reverse

start: upper_case
```

## 解析流程

```
YAML 文件
    ↓
解析 executor 定义（从注册表查找类/函数）
    ↓
实例化 Executor（UpperCase(id="upper_case")）
    ↓
WorkflowBuilder 构建连接
    ↓
.build() → Workflow 实例
    ↓
workflow.run() 执行
```

## 注册表演示

```python
registry = ExecutorRegistry()
registry.register("UpperCase", UpperCase)
registry.register("reverse", reverse_func)

# YAML 解析后
executor = registry.create("UpperCase", {"id": "upper"})
```

## Things to Remember

- **YAML 三要素**：executors（节点）、edges（连接）、start（入口）
- **type: class / function**：两种 Executor 定义方式
- **解析流程**：YAML → 注册表查找 → 实例化 → WorkflowBuilder 构建
- **YAML 是声明**：描述工作流结构，实际执行还是用代码
