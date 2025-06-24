from autogen import AssistantAgent, UserProxyAgent



# --- Configuration ---
config = {
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": "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",  # Replace with your actual key
    "model": "deepseek/deepseek-r1-0528-qwen3-8b:free"
}

# --- Define Agents ---
user = UserProxyAgent(name="Student", human_input_mode="NEVER", code_execution_config={"use_docker": False})

academic = AssistantAgent(
    name="AcademicAssistant",
    llm_config=config,
    system_message="You are an academic assistant. Answer questions about exams, GPA, study material, and academic performance."
)
career = AssistantAgent(
    name="CareerCounselor",
    llm_config=config,
    system_message="You are a career counselor. Help with resumes, job search, career paths, internships, and placement prep."
)
welfare = AssistantAgent(
    name="StudentWelfareAI",
    llm_config=config,
    system_message="You are a student welfare advisor. Talk about mental health, stress, sleep, social well-being, and motivation."
)
performance = AssistantAgent(
    name="PerformanceAnalyzer",
    llm_config=config,
    system_message="You are a performance analyzer. Interpret student data, track academic trends, and suggest improvements."
)