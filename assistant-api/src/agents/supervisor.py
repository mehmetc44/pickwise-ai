from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool

from agents.base_agent import BaseAgent
from graph.state import AgenticCommerceState
from prompts.supervisor_prompt import SUPERVISOR_SYSTEM_PROMPT


class SupervisorAgent(BaseAgent):
    """
    Ana ReAct Supervisor & Response Builder düğümü.
    """

    def __init__(self, tools: list[BaseTool]):
        super().__init__(config_key="supervisor")
        self.llm_with_tools = self.llm.bind_tools(tools)

    async def ainvoke(self, state: AgenticCommerceState) -> dict:
        messages = [SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT)] + list(state["messages"])
        ai_message = await self.llm_with_tools.ainvoke(messages)

        update: dict = {"messages": [ai_message]}
        if not getattr(ai_message, "tool_calls", None):
            update["response"] = ai_message.content if isinstance(ai_message.content, str) else str(ai_message.content)

        return update

