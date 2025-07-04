from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import time
from agents import academic, career, welfare, performance

# --- Global tracking variables ---
agent_flow_log = []
current_session_agents = []

# --- Global metrics ---
metrics_dict = {}

def reset_flow_tracking():
    """Reset tracking for a new query"""
    global agent_flow_log, current_session_agents
    agent_flow_log = []
    current_session_agents = []


def log_agent_invocation(agent_name, action, details=""):
    """Log agent invocations for flow tracking"""
    global agent_flow_log
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    agent_flow_log.append({
        "timestamp": timestamp,
        "agent": agent_name,
        "action": action,
        "details": details
    })
    if agent_name not in current_session_agents:
        current_session_agents.append(agent_name)


def display_info():
    """Display comprehensive information about agent invocations and communication flow"""
    if not agent_flow_log:
        return "No agent activity recorded for this session."

    info_output = []
    info_output.append("🤖 **AGENT FLOW ANALYSIS**")
    info_output.append("=" * 50)

    # Summary section
    info_output.append(f"📊 **Session Summary:**")
    info_output.append(f"   • Total Agents Invoked: {len(current_session_agents)}")
    info_output.append(f"   • Active Agents: {', '.join(current_session_agents)}")
    info_output.append(f"   • Total Communications: {len(agent_flow_log)}")
    info_output.append("")

    # Detailed flow
    info_output.append("🔄 **Communication Flow:**")
    for i, log_entry in enumerate(agent_flow_log, 1):
        agent_emoji = {
            "router": "🧭",
            "selector": "🎯",
            "data_context": "📊",
            "data_interpreter": "🔍",
            "academic": "📚",
            "career": "💼",
            "welfare": "🏥",
            "performance": "⚡"
        }.get(log_entry["agent"], "🤖")

        info_output.append(f"   {i}. [{log_entry['timestamp']}] {agent_emoji} **{log_entry['agent'].upper()}**")
        info_output.append(f"      Action: {log_entry['action']}")
        if log_entry['details']:
            info_output.append(f"      Details: {log_entry['details']}")
        info_output.append("")

    # Agent roles explanation
    info_output.append("📋 **Agent Roles:**")
    agent_descriptions = {
        "router": "Determines query handling strategy (lookup/llm/both)",
        "selector": "Selects appropriate specialized agents",
        "data_context": "Identifies relevant datasets",
        "data_interpreter": "Analyzes and interprets data",
        "academic": "Handles academic performance queries",
        "career": "Provides career guidance",
        "welfare": "Manages well-being concerns",
        "performance": "Focuses on performance improvement"
    }

    for agent in current_session_agents:
        if agent in agent_descriptions:
            info_output.append(f"   • **{agent}**: {agent_descriptions[agent]}")

    return "\n".join(info_output)


# --- LLM Configuration ---
config = {
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": "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",  # Use your actual API key
    "model": "deepseek/deepseek-r1-0528-qwen3-8b:free"
}

# --- User Agent ---
user = UserProxyAgent(
    name="user",
    system_message="A human user seeking help with academics, career, welfare, or performance.",
    code_execution_config=False,
    human_input_mode="NEVER"
)

# --- Specialized Agents ---
agents = {
    "academic": academic,
    "career": career,
    "welfare": welfare,
    "performance": performance,
}

# --- Router & Selector Agents ---
router_agent = AssistantAgent(
    name="router",
    system_message=(
        "You are a smart router agent. Analyze the user's question and decide how to handle it.\n"
        "Categories:\n"
        "- 'lookup': If the question asks for specific data like GPA, student records, performance metrics, or factual information from databases\n"
        "- 'llm': If the question asks for advice, recommendations, explanations, or guidance\n"
        "- 'both': If the question needs both data lookup AND reasoning/advice\n"
        "Reply with ONLY one word: 'lookup', 'llm', or 'both'"
    ),
    llm_config=config
)

selector_agent = AssistantAgent(
    name="selector",
    system_message=(
        "You are an agent selector. Based on the user query, determine which specialized agents should respond.\n"
        "Available agents:\n"
        "- 'academic': For academic performance, GPA, courses, study strategies\n"
        "- 'career': For career guidance, job prospects, professional development\n"
        "- 'welfare': For mental health, well-being, stress management\n"
        "- 'performance': For performance improvement, productivity, goal setting\n"
        "Return ONLY a Python list of agent names, e.g., ['academic'] or ['academic', 'performance']"
    ),
    llm_config=config
)

data_context_agent = AssistantAgent(
    name="data_context",
    system_message=(
        "You identify which datasets are relevant for a user query.\n"
        "Available datasets:\n"
        "- 'academic_data.csv': Student academic records, GPA, courses, warnings\n"
        "- 'performance_data.csv': Performance metrics and evaluations\n"
        "- 'welfare_data.csv': Well-being and health data\n"
        "- 'career_data.csv': Career-related information\n"
        "Return ONLY a Python list of relevant filenames, e.g., ['academic_data.csv']"
    ),
    llm_config=config
)

# Data interpretation agent
data_interpreter_agent = AssistantAgent(
    name="data_interpreter",
    system_message=(
        "You are a data interpretation specialist. Your job is to:\n"
        "1. Analyze the provided data records\n"
        "2. Extract meaningful insights relevant to the user's query\n"
        "3. Present the information in a clear, helpful format\n"
        "4. Identify patterns, trends, or specific answers to the user's question\n"
        "Always provide actionable insights based on the data."
    ),
    llm_config=config
)

# --- Load Grounded Data ---
datasets = {}
try:
    datasets = {
        "academic_data.csv": pd.read_csv("clean_academic_data.csv"),
        "performance_data.csv": pd.read_csv("performance_data_consistent.csv"),
        "welfare_data.csv": pd.read_csv("welfare_data_consistent.csv"),
        "career_data.csv": pd.read_csv("career_data_consistent.csv"),
    }
except FileNotFoundError as e:
    print(f"Warning: Could not load some datasets: {e}")


def extract_content_from_response(response):
    """Extract content from various response formats"""
    if isinstance(response, dict):
        return response.get("content") or response.get("message") or str(response)
    elif isinstance(response, list) and response:
        return response[-1].get("content") if isinstance(response[-1], dict) else str(response[-1])
    return str(response)

def tracked_generate_reply(agent, messages):
    """Wrap generate_reply to count LLM calls"""
    name = getattr(agent, 'name', 'unknown')
    metrics_dict["llm_calls"] = metrics_dict.get("llm_calls", 0) + 1
    return agent.generate_reply(messages)

def lookup_from_data(user_query):
    """Enhanced data lookup with better filtering and interpretation"""
    try:
        # Log data context agent invocation
        log_agent_invocation("data_context", "Identifying relevant datasets", f"Query: {user_query[:50]}...")

        # Get relevant datasets
        result = tracked_generate_reply(data_context_agent,[{"role": "user", "content": user_query}])
        dataset_response = extract_content_from_response(result)

        try:
            files = eval(dataset_response)
            log_agent_invocation("data_context", "Dataset selection completed", f"Selected: {files}")
        except:
            files = ["academic_data.csv"]  # Default fallback
            log_agent_invocation("data_context", "Dataset selection failed, using default", "Using academic_data.csv")

        relevant_data = []
        query_keywords = user_query.lower().split()

        for file in files:
            if file in datasets:
                df = datasets[file]

                # More intelligent data filtering
                for _, row in df.iterrows():
                    row_str = ' '.join(map(str, row.values)).lower()
                    # Check if query keywords match row content
                    if any(keyword in row_str for keyword in query_keywords):
                        relevant_data.append(row.to_dict())

                # If no specific matches, provide summary statistics for academic queries
                if not relevant_data and "academic" in user_query.lower():
                    if "gpa" in df.columns:
                        avg_gpa = df['gpa'].mean()
                        low_gpa_count = len(df[df['gpa'] < 7.0])
                        high_gpa_count = len(df[df['gpa'] >= 9.0])
                        relevant_data.append({
                            "summary": f"Academic Overview - Average GPA: {avg_gpa:.2f}, Students with GPA < 7.0: {low_gpa_count}, Students with GPA >= 9.0: {high_gpa_count}"
                        })

        if relevant_data:
            # Log data interpreter invocation
            log_agent_invocation("data_interpreter", "Interpreting data", f"Processing {len(relevant_data)} records")

            # Use data interpreter to make sense of the data
            data_str = json.dumps(relevant_data, indent=2)
            interpretation_query = f"User asked: '{user_query}'\n\nRelevant data found:\n{data_str}\n\nPlease provide insights and actionable advice based on this data."

            interpretation_result = tracked_generate_reply(
                data_interpreter_agent,[{"role": "user", "content": interpretation_query}])
            log_agent_invocation("data_interpreter", "Data interpretation completed",
                                 "Generated insights and recommendations")
            return extract_content_from_response(interpretation_result)

        log_agent_invocation("data_context", "No relevant data found", "No matching records in datasets")
        return None
    except Exception as e:
        log_agent_invocation("data_context", "Error occurred", f"Error: {str(e)}")
        print(f"Data lookup error: {e}")
        return None


# --- DB Setup ---
def init_db():
    conn = sqlite3.connect("edutrack_logs.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_query TEXT,
                        agent_response TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')

    # Check if agent_flow column exists, if not add it
    cursor.execute("PRAGMA table_info(logs)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'agent_flow' not in columns:
        cursor.execute("ALTER TABLE logs ADD COLUMN agent_flow TEXT")
        print("Added agent_flow column to existing database")

    conn.commit()
    conn.close()


init_db()


def log_interaction(user_query, agent_response, agent_flow_info=None):
    conn = sqlite3.connect("edutrack_logs.db")
    cursor = conn.cursor()

    # Handle cases where agent_flow_info might be None (backward compatibility)
    if agent_flow_info is None:
        agent_flow_info = "No flow information available"

    cursor.execute(
        "INSERT INTO logs (user_query, agent_response, agent_flow) VALUES (?, ?, ?)",
        (user_query, agent_response, agent_flow_info)
    )
    conn.commit()
    conn.close()


def classify_query(user_query):
    """Enhanced query classification"""
    try:
        log_agent_invocation("router", "Classifying query", f"Analyzing: {user_query[:50]}...")

        decision = tracked_generate_reply(router_agent, [{"role": "user", "content": user_query}])
        classification = extract_content_from_response(decision).strip().lower()

        # Ensure valid classification
        if classification not in ["lookup", "llm", "both"]:
            # Default logic based on keywords
            if any(keyword in user_query.lower() for keyword in
                   ["what is my", "show me", "find", "gpa", "records", "data"]):
                classification = "lookup"
            elif any(
                    keyword in user_query.lower() for keyword in ["how to", "improve", "advice", "help me", "suggest"]):
                classification = "llm"
            else:
                classification = "both"

        log_agent_invocation("router", "Classification completed", f"Result: {classification}")
        return classification
    except Exception as e:
        log_agent_invocation("router", "Classification error", f"Error: {str(e)}")
        print(f"Classification error: {e}")
        return "llm"  # Default fallback


def route_to_agents(user_query):
    """Enhanced agent routing"""
    try:
        log_agent_invocation("selector", "Selecting agents", f"Analyzing query for agent selection")

        result = tracked_generate_reply( selector_agent, [{"role": "user", "content": user_query}])
        selector_response = extract_content_from_response(result)

        try:
            selected = eval(selector_response)
            log_agent_invocation("selector", "Agent selection completed", f"Selected: {selected}")
        except:
            # Fallback logic based on keywords
            if any(keyword in user_query.lower() for keyword in ["academic", "study", "gpa", "course", "grade"]):
                selected = ["academic"]
            elif any(keyword in user_query.lower() for keyword in ["career", "job", "work", "professional"]):
                selected = ["career"]
            elif any(keyword in user_query.lower() for keyword in
                     ["stress", "mental", "health", "wellbeing", "welfare"]):
                selected = ["welfare"]
            elif any(keyword in user_query.lower() for keyword in ["performance", "improve", "productivity", "goal"]):
                selected = ["performance"]
            else:
                selected = ["academic"]  # Default
            log_agent_invocation("selector", "Fallback selection used", f"Selected: {selected}")

        return [agents[agent_name] for agent_name in selected if agent_name in agents]
    except Exception as e:
        log_agent_invocation("selector", "Selection error", f"Error: {str(e)}")
        print(f"Routing error: {e}")
        return [agents["academic"]]  # Default fallback


def get_single_agent_response(agent, user_query, context_data=None):
    """Enhanced single agent response with context"""
    try:
        agent_name = getattr(agent, 'name', 'unknown_agent')
        log_agent_invocation(agent_name, "Generating response", "Single agent mode")

        # Add context data if available
        enhanced_query = user_query
        if context_data:
            enhanced_query = f"Context data: {context_data}\n\nUser query: {user_query}\n\nPlease provide advice considering both the context data and the user's question."

        response = tracked_generate_reply(agent, [{"role": "user", "content": enhanced_query}])
        log_agent_invocation(agent_name, "Response completed", f"Generated response length: {len(str(response))} chars")
        return extract_content_from_response(response)
    except Exception as e:
        agent_name = getattr(agent, 'name', 'unknown_agent')
        log_agent_invocation(agent_name, "Response error", f"Error: {str(e)}")
        return f"Error from {agent_name}: {e}"


def get_multiple_agent_responses(selected_agents, user_query, context_data=None):
    """Enhanced multiple agent responses"""
    try:
        agent_names = [getattr(agent, 'name', 'unknown') for agent in selected_agents]
        log_agent_invocation("group_chat", "Initiating group chat", f"Agents: {agent_names}")

        # Prepare enhanced query with context
        enhanced_query = user_query
        if context_data:
            enhanced_query = f"Context: {context_data}\n\nQuery: {user_query}"

        group = GroupChat(
            agents=[user] + selected_agents,
            messages=[],
            max_round=3,
            speaker_selection_method="auto"
        )
        manager = GroupChatManager(groupchat=group, llm_config=config)
        user.initiate_chat(manager, message=enhanced_query, max_turns=3)

        log_agent_invocation("group_chat", "Group chat completed", f"Total messages: {len(group.messages)}")

        messages = [msg for msg in group.messages if msg.get("role") == "assistant"]
        if messages:
            return "\n\n".join([f"**{msg.get('name', 'Assistant')}**: {msg['content']}" for msg in messages])
        else:
            log_agent_invocation("group_chat", "Fallback to individual responses", "Group chat produced no messages")
            # Fallback to individual responses
            return "\n\n".join([
                f"**{getattr(agent, 'name', 'agent')}**: {get_single_agent_response(agent, user_query, context_data)}"
                for agent in selected_agents
            ])
    except Exception as e:
        log_agent_invocation("group_chat", "Group chat failed", f"Error: {str(e)}")
        print(f"Group chat failed: {e}")
        # Fallback to individual responses
        return "\n\n".join([
            f"**{getattr(agent, 'name', 'agent')}**: {get_single_agent_response(agent, user_query, context_data)}"
            for agent in selected_agents
        ])


def hybrid_response(user_query):
    reset_flow_tracking()
    metrics_dict.clear()  # reset metrics per query
    metrics_dict["start_time"] = time.time()


    log_agent_invocation("system", "Query received", f"Processing: {user_query}")

    mode = classify_query(user_query)

    data_response = None
    agent_response = None

    if mode in ["lookup", "both"]:
        data_response = lookup_from_data(user_query)

    if mode in ["llm", "both"]:
        selected_agents = route_to_agents(user_query)
        metrics_dict["agents_invoked"] = len(selected_agents)
        if len(selected_agents) == 1:
            agent_response = get_single_agent_response(selected_agents[0], user_query, data_response)
        elif selected_agents:
            agent_response = get_multiple_agent_responses(selected_agents, user_query, data_response)

    metrics_dict["end_time"] = time.time()
    metrics_dict["total_time"] = round(metrics_dict["end_time"] - metrics_dict["start_time"], 3)

    log_agent_invocation("system", "Response generation completed", f"Mode: {mode}")

    if data_response and agent_response:
        if mode == "both":
            return f"**Data Insights:**\n{data_response}\n\n**Recommendations:**\n{agent_response}"
        else:
            return agent_response
    elif data_response:
        return data_response
    elif agent_response:
        return agent_response
    else:
        return "I couldn't find relevant information or generate a helpful response. Please rephrase your question."


# --- FastAPI ---
app = FastAPI()


class Query(BaseModel):
    message: str


@app.post("/ask")
async def ask_edutrack(query: Query):
    response = hybrid_response(query.message)
    flow_info = display_info()
    log_interaction(query.message, response, flow_info)
    return {"response": response, "agent_flow": flow_info}


# --- Streamlit Frontend ---
st.set_page_config(page_title="Edutrack AI Chatbot", page_icon="📚")
st.title("📚 Edutrack")
st.markdown("*Your AI-powered educational assistant*")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

with col2:
    show_agent_flow = st.checkbox("Show Agent Flow", value=False)

with col3:
    if st.button("Show Sample Questions"):
        st.info("""
        **Sample Questions:**
        - How can I improve my academic performance?
        - What's my current GPA status?
        - Show me students with academic warnings
        - Give me career advice for my major
        - How to manage academic stress?
        - What are effective study strategies?
        """)

user_input = st.text_input("Ask something about your academics, career, well-being, or performance:")

if user_input:
    with st.spinner("Analyzing your question and preparing response..."):
        response = hybrid_response(user_input)
        flow_info = display_info()
        st.session_state.chat_history.append((user_input, response, flow_info))
        log_interaction(user_input, response, flow_info)

# Display chat history
st.markdown("---")
if st.session_state.chat_history:
    st.subheader("Chat History")
    for i, (q, r, flow) in enumerate(reversed(st.session_state.chat_history)):
        with st.container():
            st.markdown(f"**You:** {q}")
            st.markdown(f"**Edutrack:** {r}")

            with st.expander("📊 Metrics (Domain agents)"):
                st.markdown(f"- **Total Time Taken:** {metrics_dict.get('total_time', 'N/A')} sec")
                st.markdown(f"- **Agents Invoked:** {metrics_dict.get('agents_invoked', 'N/A')}")
                st.markdown(f"- **LLM Calls:** {metrics_dict.get('llm_calls', 'N/A')}")

            if show_agent_flow:
                with st.expander("🔍 View Agent Flow Details"):
                    st.text(flow)

            if i < len(st.session_state.chat_history) - 1:
                st.markdown("---")
else:
    st.info("Start a conversation by asking a question above!")