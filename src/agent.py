"""Core agent logic for Government Data Discovery Assistant."""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

from tools import list_data_categories, get_category_questions, search_data_gov_datasets

class Agent:
    def __init__(self):
        self.name = "Government Data Discovery Assistant"

        self.tools = [
            list_data_categories,
            get_category_questions,
            search_data_gov_datasets,
        ]

        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a Government Data Discovery Assistant for data.gov.in.

Your workflow:
1) Understand the user's goal.
2) Identify likely category (agriculture, health, education, transport, etc.).
3) If request is ambiguous, ask category-wise clarifying questions using get_category_questions.
4) Once enough context is available, call search_data_gov_datasets.
5) Return concise, practical results and suggest improved follow-up queries.

Rules:
- Prefer asking 2-4 targeted questions before searching when location/time/topic is unclear.
- Always help users refine query into strong context: topic + geography + timeframe + indicator.
- If API key is missing, explain exactly which env var to set: DATAGOVINDIA_API_KEY.
- Keep responses concise and action-oriented.
""",
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def process_message(self, message_text: str) -> str:
        """Process incoming user message through the tool-calling agent."""
        result = self.agent_executor.invoke({"input": message_text})
        return result["output"]
