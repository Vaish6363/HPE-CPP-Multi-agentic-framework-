from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager 
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import re
import streamlit as st
from keyword_map import keyword_map
from agents import academic, career, welfare, performance

# --- LLM Configuration ---
config = {
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": "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",  
    "model": "deepseek/deepseek-r1-0528-qwen3-8b:free"
}

# --- Create User Proxy Agent ---
user = UserProxyAgent(
    name="user",
    system_message="A human user seeking help with academics, career, welfare, or performance.",
    code_execution_config=False,
    human_input_mode="NEVER"
)

# --- Agent List and Keyword Routing ---
agents = [academic, career, welfare, performance]

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("edutrack_logs.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_query TEXT,
                        agent_response TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
    conn.commit()
    conn.close()

init_db()

def log_interaction(user_query, agent_response):
    conn = sqlite3.connect("edutrack_logs.db")
    cursor = conn.cursor()

    # Convert agent_response to string if it's not
    if not isinstance(agent_response, str):
        agent_response = str(agent_response)

    cursor.execute(
        "INSERT INTO logs (user_query, agent_response) VALUES (?, ?)",
        (user_query, agent_response)
    )
    conn.commit()
    conn.close()

# --- Utility Functions ---
def identify_agents(user_query):
    matched_agents = set()
    user_query_lower = user_query.lower()
    
    # Check for keywords in the query
    for keyword, agent in keyword_map.items():
        if keyword.lower() in user_query_lower:
            matched_agents.add(agent)
    
    # Additional logic for better matching
    if any(word in user_query_lower for word in ['grade', 'gpa', 'cgpa', 'academic', 'study', 'exam', 'course', 'subject', 'dsa', 'algorithm', 'marks', 'score']):
        matched_agents.add(academic)
    
    if any(word in user_query_lower for word in ['career', 'job', 'internship', 'analyst', 'data analyst', 'profession', 'work', 'interview']):
        matched_agents.add(career)
    
    if any(word in user_query_lower for word in ['performance', 'improve', 'weak', 'better', 'progress', 'skills', 'enhancement']):
        matched_agents.add(performance)
    
    if any(word in user_query_lower for word in ['stress', 'anxiety', 'mental', 'health', 'wellbeing', 'welfare', 'motivation']):
        matched_agents.add(welfare)
    
    return list(matched_agents)

def get_single_agent_response(agent, user_query):
    """Get response from a single agent with improved error handling"""
    try:
        # Generate reply from agent
        response = agent.generate_reply([{"role": "user", "content": user_query}])
        
        # Handle None response
        if response is None:
            agent_name = getattr(agent, 'name', 'Agent')
            return f"Sorry, {agent_name} couldn't generate a response. Please try rephrasing your question."
        
        # Handle different response types
        if isinstance(response, dict):
            if 'content' in response:
                return response['content']
            elif 'message' in response:
                return response['message']
            else:
                # If it's a dict but no expected keys, convert to string
                return str(response)
        elif isinstance(response, str):
            return response
        elif isinstance(response, list):
            # Handle list responses (sometimes agents return message lists)
            if len(response) > 0:
                last_message = response[-1]
                if isinstance(last_message, dict) and 'content' in last_message:
                    return last_message['content']
                else:
                    return str(last_message)
            else:
                return "No response generated."
        else:
            return str(response)
            
    except Exception as e:
        agent_name = getattr(agent, 'name', 'Agent')
        return f"Error getting response from {agent_name}: {str(e)}"

def get_multiple_agent_responses(selected_agents, user_query):
    """Get responses from multiple agents - improved version"""
    responses = []
    
    # Try group chat first
    try:
        # Create a fresh group chat
        group = GroupChat(
            agents=[user] + selected_agents, 
            messages=[], 
            max_round=2,  # Reduced rounds for stability
            speaker_selection_method="round_robin"
        )
        manager = GroupChatManager(groupchat=group, llm_config=config)
        
        # Initialize the chat
        chat_result = user.initiate_chat(
            manager, 
            message=user_query,
            max_turns=2
        )
        
        # Extract responses from the group chat
        if hasattr(group, 'messages') and group.messages:
            assistant_messages = [
                msg for msg in group.messages 
                if msg.get("role") == "assistant" and msg.get("content")
            ]
            
            if assistant_messages:
                # Combine all assistant responses
                combined_response = "\n\n".join([
                    f"**{msg.get('name', 'Assistant')}:** {msg.get('content')}"
                    for msg in assistant_messages
                ])
                return combined_response
    
    except Exception as e:
        print(f"Group chat failed: {str(e)}")
    
    # Fallback: Get individual responses
    for agent in selected_agents:
        try:
            agent_response = get_single_agent_response(agent, user_query)
            agent_name = getattr(agent, 'name', 'Agent')
            responses.append(f"**{agent_name}:** {agent_response}")
        except Exception as agent_error:
            agent_name = getattr(agent, 'name', 'Agent')
            responses.append(f"**{agent_name}:** Error - {str(agent_error)}")
    
    return "\n\n".join(responses) if responses else "Unable to generate responses from agents."

# --- FastAPI Setup ---
app = FastAPI()

class Query(BaseModel):
    message: str

@app.post("/ask")
async def ask_edutrack(query: Query):
    user_query = query.message
    selected_agents = identify_agents(user_query)

    if not selected_agents:
        response = "Please provide more context so I can help you better with your academics, career, performance, or wellbeing."
    elif len(selected_agents) == 1:
        response = get_single_agent_response(selected_agents[0], user_query)
    else:
        response = get_multiple_agent_responses(selected_agents, user_query)

    log_interaction(user_query, response)
    return {"response": response}

# --- Streamlit Frontend ---
st.set_page_config(page_title="Edutrack AI Chatbot", page_icon="📚")
st.title("📚 Edutrack")
st.markdown("*Your AI-powered assistant*")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

# User input
user_input = st.text_input("Ask something about your academics, career, well-being, or performance:")

if user_input:
    with st.spinner("Getting response..."):
        selected_agents = identify_agents(user_input)
        
        # Debug information (can be removed in production)
        with st.expander("Debug Info"):
            st.write(f"Selected agents: {[getattr(agent, 'name', str(agent)) for agent in selected_agents]}")

        if not selected_agents:
            response = "Please provide more context so I can help you better with your academics, career, performance, or wellbeing."
        elif len(selected_agents) == 1:
            response = get_single_agent_response(selected_agents[0], user_input)
        else:
            response = get_multiple_agent_responses(selected_agents, user_input)

        # Add to chat history
        st.session_state.chat_history.append((user_input, response))
        log_interaction(user_input, response)

# Display chat history
st.markdown("---")
for i, (q, r) in enumerate(reversed(st.session_state.chat_history)):
    with st.container():
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Edutrack:** {r}")
        if i < len(st.session_state.chat_history) - 1:
            st.markdown("---")




# --- Run the application ---
if __name__ == "__main__":
    # For FastAPI
    # import uvicorn
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    # For Streamlit
    # Run with: streamlit run your_script_name.py
    pass