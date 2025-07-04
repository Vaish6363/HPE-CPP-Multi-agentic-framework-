from autogen import AssistantAgent, UserProxyAgent



# --- Configuration ---
config = {
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": "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",  # Replace with your actual key
    "model": "deepseek/deepseek-r1-0528-qwen3-8b:free"
}

# --- Define Agents ---
user = UserProxyAgent(
    name="Student",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False}
)
academic = AssistantAgent(
    name="academic",
    system_message=(
        "You are the academic advisor. You help with courses, exams, GPA, and study advice.\n"
        "If the user's question includes emotions, anxiety, or motivation, involve the 'welfare' agent.\n"
        "If the user needs job guidance or future planning, involve the 'career' agent.\n"
        "Coordinate with other agents when appropriate to provide a complete and personalized support strategy."
        
    ),
    llm_config=config
)
career = AssistantAgent(
    name="career",
    system_message=(
        "You are the career advisor. You help with internships, resumes, job preparation, and skills.\n"
        "If the user is struggling academically, suggest talking with the 'academic' agent.\n"
        "If they mention burnout or stress, suggest involving the 'welfare' agent."
    ),
    llm_config=config
)
welfare = AssistantAgent(
    name="welfare",
    system_message=(
        "You are the welfare advisor. You handle mental health, motivation, stress, and well-being.\n"
        "If the user mentions failing or poor academic performance, suggest involving the 'academic' agent.\n"
        "If the user expresses hopelessness or uncertainty about the future, involve the 'career' agent."
    ),
    llm_config=config
)
performance = AssistantAgent(
    name="performance",
    system_message=(
        "You are the performance improvement advisor. Your focus is helping users enhance their learning efficiency, "
        "overcome weaknesses, build habits, and reach their academic or personal development goals.\n\n"
        "If the user talks about low grades or poor exam results, suggest involving the 'academic' agent.\n"
        "If the user is feeling demotivated, overwhelmed, or burnt out, consider involving the 'welfare' agent.\n"
        "If the user is trying to improve job readiness, soft skills, or productivity at work, invite the 'career' agent.\n\n"
        "Coordinate with other agents when appropriate to provide a complete and personalized support strategy."
    ),
    llm_config=config
)