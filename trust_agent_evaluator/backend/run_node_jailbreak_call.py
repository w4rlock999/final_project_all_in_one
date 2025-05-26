import os
import langchain_openai
from dotenv import load_dotenv
from node_jailbreak_call import NodeJailbreakCall

load_dotenv()

def main():
    # Initialize the LLM for jailbreak testing
    llm = langchain_openai.ChatOpenAI(
        model="deepseek/deepseek-chat",
        openai_api_key=os.getenv("DEEPSEEK_OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2
    )

    # Initialize the jailbreak test with the graph data
    jailbreaking_test = NodeJailbreakCall(llm, './data/output/detailed_graph.json')

    # Run the jailbreak tests
    jailbreaking_test.test_jailbreaking(jailbreak_test_attempts=30)

if __name__ == "__main__":
    main()

    