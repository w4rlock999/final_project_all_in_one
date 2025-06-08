import os
import json
import langchain_openai
from dotenv import load_dotenv
from jailbreak_judge import JailbreakJudge

load_dotenv()

def main():
    # Initialize the judge LLM
    judge_llm = langchain_openai.ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Load jailbreak prompts
    with open('./jailbreak_prompts.json', 'r', encoding='utf-8') as f:
        jailbreak_prompts_data = json.load(f)
        jailbreak_prompts = [jailbreak_prompt['prompt'] for jailbreak_prompt in jailbreak_prompts_data['prompts']]

    # Initialize the judge
    judge = JailbreakJudge(judge_llm, jailbreak_prompts)

    # Judge the jailbreak results
    judge.judge_jailbreak_success('./data/output/jailbreak_results.json')

    # Update the graph with success rates
    judge.update_graph_with_success_rates(
        judge_results_file='./data/output/jailbreak_judge_result.json',
        graph_file='./data/output/detailed_graph.json',
        output_file='./data/output/detailed_graph_with_jb.json'
    )

if __name__ == "__main__":
    main() 