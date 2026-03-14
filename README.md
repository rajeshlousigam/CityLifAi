# Government Data Discovery Agent

This project is an A2A-compatible assistant that helps users discover and query public datasets from `data.gov.in`.

It uses the Python wrapper `datagovindia` and guides users with category-wise clarifying questions so they can ask context-rich queries.

## Features

- **Category Guidance**: Suggests likely category from user intent (agriculture, health, education, transport, etc.)
- **Question Framework**: Asks category-wise clarifying questions (location, timeframe, indicator, granularity)
- **Dataset Discovery**: Searches and returns relevant `data.gov.in` datasets with source and links
- **Conversational Interface**: Natural language interaction powered by LangChain tool-calling

## Categories Supported

- agriculture
- health
- education
- transport
- environment
- economy
- employment
- energy
- housing
- demographics
- crime
- tourism

## Frameworks
- **Server**: FastAPI
- **Agent Logic**: LangChain with OpenAI GPT-4
- **Protocol**: A2A JSON-RPC 2.0

## Structure

- `src/__main__.py`: FastAPI server handling A2A JSON-RPC `message/send` requests
- `src/models.py`: A2A protocol Pydantic models (Message, Task, etc.)
- `src/tools.py`: data.gov.in tools (`list_data_categories`, `get_category_questions`, `search_data_gov_datasets`)
- `src/agent.py`: Government data assistant prompt and tool-calling workflow
- `AgentCard.json`: Agent metadata and capabilities
- `Dockerfile`: Docker configuration

## How to Run

1. **Set API Keys**:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
  export DATAGOVINDIA_API_KEY=your_datagovindia_api_key
   ```

2. **Build and Run with Docker**:
   ```bash
  docker build -t gov-data-agent .
  docker run -p 5000:5000 \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -e DATAGOVINDIA_API_KEY=$DATAGOVINDIA_API_KEY \
    gov-data-agent
   ```

3. **Test the Agent**:
   ```bash
   curl -X POST http://localhost:5000/ \
   -H "Content-Type: application/json" \
   -d '{
     "jsonrpc": "2.0",
     "id": "1",
     "method": "message/send", 
     "params": {
       "message": {
         "role": "user",
        "parts": [{"kind": "text", "text": "Find crop production datasets for Karnataka for the last 5 years"}]
       }
     }
   }'
   ```

## Example Interactions

- "I need crop production datasets for Karnataka for the last 5 years."
- "Find district-level air quality datasets for Delhi between 2020 and 2024."
- "Help me choose the right category for vaccination coverage data."
- "What questions should I answer before searching education outcome data?"

## Customization

To modify this agent for your own use case:

1. **Edit `src/tools.py`**: Add your own tools using the `@tool` decorator
2. **Edit `src/agent.py`**: Customize the system prompt and agent behavior  
3. **Update `AgentCard.json`**: Modify agent metadata and capabilities
4. **Update Dockerfile**: Add any additional dependencies

