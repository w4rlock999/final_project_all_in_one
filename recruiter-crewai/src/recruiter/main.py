#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from recruiter.crew import Recruiter
import os
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

import os
# import base64
# import openlit
 
# Local Langfuse
# LANGFUSE_SECRET_KEY="sk-lf-6c7f1d9c-9dc6-4061-bb81-a77b9b3d5ffe"
# LANGFUSE_PUBLIC_KEY="pk-lf-dd1577e9-be42-4bc0-9cb6-73fd709f3cf9"
# LANGFUSE_HOST="http://localhost:3000"

# LANGFUSE_AUTH=base64.b64encode(f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()).decode()
import mlflow

def run():
    """
    Run the crew.
    """
    inputs = {        
        'current_year': str(datetime.now().year),
        'path_to_cv': '../data/cv1.md',
        'path_to_job_desc': '../data/job1.md'
    }

    # Generate a unique session ID using timestamp
    # session_id = f"recruiter_session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"    
    # langfuse_context.update_current_trace(
    #     session_id=session_id
    # )    
    # os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:3000/api/public/otel" # local
    # os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

    # openlit.init()

    try:
        Recruiter().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'current_year': str(datetime.now().year)
    }
    try:
        Recruiter().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Recruiter().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'current_year': str(datetime.now().year)
    }
    try:
        Recruiter().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
