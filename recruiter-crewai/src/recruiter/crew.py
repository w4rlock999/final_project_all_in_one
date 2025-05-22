from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_community.tools import DuckDuckGoSearchRun
from crewai.tools import tool
from crewai_tools import FileReadTool

from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from crewai import LLM
import os

from datetime import datetime

class EmailSenderInput(BaseModel):
	"""Input schema for EmailSenderTool"""
	email_address: str = Field(..., description="email address of the receiver")
	email_text: str = Field(..., description="email text for the receiver")

class EmailSenderTool(BaseTool):
    name: str = "Email sender tool"
    description: str = "Sending email text message to the receiver email address"
    args_schema: Type[BaseModel] = EmailSenderInput

    def _run(self, email_address: str, email_text: str) -> str:
		# nothing, just a dummy tool
        return "Successfully sending email to {email_address}..."	

@tool('DuckDuckGoSearch')
def search(search_query: str):
	"""Search the web for information on a given topic such as tech job market trend, relevant tech skills, etc."""
	return DuckDuckGoSearchRun().run(search_query)


email_sender_tool = EmailSenderTool()
file_read_tool = FileReadTool()

# define deepseek
# deepseek_llm = LLM(
#     model="deepseek/deepseek-reasoner",
#     api_key=os.getenv("DEEPSEEK_API_KEY"),
# 	temperature=0.2
# )

deepseek_llm = LLM(
    model="openrouter/deepseek/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_OPENROUTER_API_KEY"),
	temperature=0.2
)

# deepseek_llm = LLM(model="ollama/deepseek-r1:8b", base_url="http://localhost:11434", temperature=0.2)

@CrewBase
class Recruiter():
	"""Recruiter crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# ===========================================================================
	# ============================    Agents   ==================================
	# ===========================================================================

	@agent
	def recruitment_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['recruitment_analyst'],
			verbose=True,
			tools=[search, file_read_tool],
			llm=deepseek_llm
		)

	@agent
	def job_profiler(self) -> Agent:
		return Agent(
			config=self.agents_config['job_profiler'],
			verbose=True,
			tools=[search, file_read_tool],
			llm=deepseek_llm
		)

	@agent
	def hiring_candidate_evaluator(self) -> Agent:
		return Agent(
			config=self.agents_config['hiring_candidate_evaluator'],
			verbose=True,
			llm=deepseek_llm
		)

	@agent
	def tech_company_communication_department(self) -> Agent:
		return Agent(
			config=self.agents_config['tech_company_communication_department'],
			verbose=True,
			tools=[email_sender_tool, file_read_tool],
			llm=deepseek_llm
		)

	# ===========================================================================
	# ============================    Tasks    ==================================
	# ===========================================================================


	@task
	def cv_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['cv_analysis_task'],
			agent=self.recruitment_analyst(),			
		)

	@task
	def job_description_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['job_description_analysis_task'],
			agent=self.recruitment_analyst(),
			context=[],
		)

	@task
	def job_profile_creation_task(self) -> Task:
		return Task(
			config=self.tasks_config['job_profile_creation_task'],
			agent=self.job_profiler(),
			context=[self.job_description_analysis_task()]
		)

	@task
	def candidate_fitness_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['candidate_fitness_analysis_task'],
			agent=self.recruitment_analyst(),
			context=[self.cv_analysis_task(), self.job_description_analysis_task(), self.job_profile_creation_task()]
		)

	@task
	def recruitment_scoring_builder(self) -> Task:
		return Task(
			config=self.tasks_config['recruitment_scoring_builder'],
			agent=self.recruitment_analyst(),
			context=[self.job_description_analysis_task(), self.job_profile_creation_task()]
		)

	@task
	def candidate_fitness_scoring_and_decision_task(self) -> Task:
		return Task(
			config=self.tasks_config['candidate_fitness_scoring_and_decision_task'],
			agent=self.hiring_candidate_evaluator(),
			context=[self.candidate_fitness_analysis_task(), self.recruitment_scoring_builder()]
		)

	@task
	def candidate_email_communication_task(self) -> Task:
		return Task(
			config=self.tasks_config['candidate_email_communication_task'],
			agent=self.tech_company_communication_department(),
			context=[self.candidate_fitness_scoring_and_decision_task()]
		)
	

	# ===========================================================================
	# ============================     Crew    ==================================
	# ===========================================================================	


	@crew
	def crew(self) -> Crew:
		"""Creates the Recruiter crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		session_id = f"recruiter_session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			custom_metadata={
				"session_id": "4May2025"
			}
		)
