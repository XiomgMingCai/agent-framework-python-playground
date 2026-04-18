# Copyright (c) Microsoft. All rights reserved.
# Based on: https://learn.microsoft.com/en-us/agent-framework/get-started/workflows
# Step 5: Workflows - 链式调用多个步骤的工作流

import asyncio

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler, executor


# Step 1: A class-based executor that converts text to uppercase
class UpperCase(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def to_upper_case(self, text: str, ctx: WorkflowContext[str]) -> None:
        """Convert input to uppercase and forward to the next node."""
        await ctx.send_message(text.upper())


# Step 2: A function-based executor that reverses the string and yields output
@executor(id="reverse_text")
async def reverse_text(text: str, ctx: WorkflowContext[str]) -> None:
    """Reverse the string and yield the final workflow output."""
    await ctx.yield_output(text[::-1])


def create_workflow():
    """Build the workflow: UpperCase → reverse_text."""
    upper = UpperCase(id="upper_case")
    return WorkflowBuilder(start_executor=upper).add_edge(upper, reverse_text).build()


async def main():
    workflow = create_workflow()

    print("=" * 60)
    print("  Workflow Demo: UpperCase → ReverseText")
    print("=" * 60)

    test_cases = ["hello world", "Python"]

    for test_input in test_cases:
        print(f'\nInput: "{test_input}"')
        print("         ↓")
        print("    UpperCase 步骤")
        print("    (转换为大写)")
        print("         ↓")

        events = await workflow.run(test_input)
        outputs = events.get_outputs()
        upper_output = test_input.upper()
        final_output = outputs[0] if outputs else ""

        print(f'     "{upper_output}"')
        print("         ↓")
        print("   ReverseText 步骤")
        print("    (翻转字符串)")
        print("         ↓")
        print(f'   Output: "{final_output}"')


if __name__ == "__main__":
    asyncio.run(main())
