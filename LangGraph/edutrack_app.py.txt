%%writefile edutrack_app.py
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import pandas as pd
from typing import TypedDict, Annotated
import streamlit as st
import datetime
import re
import time

# --- LLM Configuration ---
llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",
    api_key="YOUR_KEY"
)

# --- Load Datasets ---
datasets = {
    "academic": pd.read_csv("academic_refined.csv"),
    "performance": pd.read_csv("performance_refined.csv"),
    "welfare": pd.read_csv("welfare_refined.csv"),
    "career": pd.read_csv("career_refined.csv")
}

# --- State Structure ---
class AgentState(TypedDict):
    question: Annotated[str, "input"]
    user_data: Annotated[dict, "input"]
    messages: Annotated[list[dict], "accumulate"]
    completed_agents: Annotated[list[str], "accumulate"]
    academic_response: Annotated[str, "output"]
    career_response: Annotated[str, "output"]
    wellness_response: Annotated[str, "output"]
    performance_response: Annotated[str, "output"]
    agent_log: Annotated[list[dict], "accumulate"]
    next: Annotated[str, "internal"]

# --- Utility ---
def log(agent, action, details, state):
    state["agent_log"].append({
        "timestamp": str(datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]),
        "agent": agent,
        "action": action,
        "details": details
    })

def extract_user_data(question: str, state: AgentState) -> dict:
    log("router", "Query received", f"Processing \"{question}\"", state)
    match = re.search(r'\b\d{4,}\b', question)
    student_id = match.group(0) if match else None

    combined_data = {}
    
    log("data_context", "Identifying relevant datasets", "Looking for matches", state)
    
    for name, df in datasets.items():
        df.columns = df.columns.str.strip().str.lower()  # Normalize column names
        if student_id and "student_id" in df.columns:
            row = df[df["student_id"].astype(str) == student_id]
            if not row.empty:
                combined_data.update(row.iloc[0].to_dict())
                log("data_interpreter", "Data interpreted", f"Matched ID {student_id} in {name}_refined.csv", state)
        elif "name" in df.columns:
            for _, row in df.iterrows():
                if row["name"].lower() in question.lower():
                    combined_data.update(row.to_dict())
                    log("data_interpreter", "Data interpreted", f"Matched name in {name}_refined.csv", state)
                    break

    return combined_data


def detect_agents(question: str, state: AgentState):
    log("router", "Classifying query", "Analyzing keywords", state)
    prompt = ChatPromptTemplate.from_template('''
You are an intelligent agent router. Given a student's query, choose the most relevant support agents to activate **based on the content**.

Here's what each agent does:
- academic_agent: For questions about GPA, study tips, courses, time management.
- career_agent: For career guidance, internships, job readiness, resume, skills.
- wellness_agent: For issues related to mental health, sleep, stress, well-being.
- performance_agent: For test scores, assignments, improvement, marks.

Only return the agent names that apply, separated by commas. No explanation.

Query: "{question}"
Agents:
''')
    result = (prompt | llm).invoke({"question": question})
    agents = [a.strip() for a in result.content.split(',') if a.strip() in ["academic_agent", "career_agent", "wellness_agent", "performance_agent"]]
    log("router", "Classification completed", f"Detected agent(s): {', '.join(agents)}", state)
    log("selector", "Agent selection completed", f"{', '.join(agents)}", state)
    return agents

# --- Shared Prompt Function ---
def build_agent_prompt(agent_name: str, summary: str, role_instruction: str):
    return ChatPromptTemplate.from_template(f"""
You are the {agent_name.replace('_', ' ').title()}. Read the full message history and collaborate with other agents.

### Student Profile Summary:
{summary}

### Conversation History:
{{prior}}

### Student Query:
{{question}}

{role_instruction}
""")

# --- Example Agent ---
def performance_agent(state: AgentState):
    prior = "\n".join([f"{m['sender']}: {m['content']}" for m in state["messages"]]) if state["messages"] else "No prior context"
    user = state["user_data"]
    summary = f"""
📊 Performance Profile for {user.get('name', 'Student')}
- GPA: {user.get('gpa', 'NA')}
- Weak Subjects: {user.get('weak_subjects', 'NA')}
- Strengths: {user.get('strengths', 'NA')}
- Recent Progress: {user.get('recent_progress', 'NA')}
"""
    prompt = build_agent_prompt("performance_agent", summary, """
Provide:
1. Overall performance assessment
2. Plan to improve weak areas
3. Boost strengths
4. Suggestions aligned with academic/career advice.
""")
    response = (prompt | llm).invoke({"question": state["question"], "prior": prior}).content
    full = summary + "\n---\n" + response
    state["messages"].append({"sender": "PerformanceAgent", "content": full})
    state["completed_agents"].append("performance_agent")
    state["performance_response"] = full
    log("performance_agent", "Response generated", f"Response length: {len(response)} chars", state)
    return state

def academic_agent(state: AgentState):
    prior = "\n".join([f"{m['sender']}: {m['content']}" for m in state["messages"]]) if state["messages"] else "No prior context"
    user = state["user_data"]
    summary = f"""
📘 Academic Profile for {user.get('name', 'Student')}
- GPA: {user.get('gpa', 'NA')}
- Academic Warnings: {user.get('academic_warnings', 'NA')}
- Major: {user.get('major', 'NA')}
- Current Courses: {user.get('current_courses', 'NA')}
"""
    prompt = build_agent_prompt("academic_agent", summary, """
Offer:
1. Feedback on academic progress
2. Time management & study strategy suggestions
3. Course recommendations or areas to focus on
""")
    response = (prompt | llm).invoke({"question": state["question"], "prior": prior}).content
    full = summary + "\n---\n" + response
    state["messages"].append({"sender": "AcademicAgent", "content": full})
    state["completed_agents"].append("academic_agent")
    state["academic_response"] = full
    log("academic_agent", "Response generated", f"Response length: {len(response)} chars", state)
    return state

def career_agent(state: AgentState):
    prior = "\n".join([f"{m['sender']}: {m['content']}" for m in state["messages"]]) if state["messages"] else "No prior context"
    user = state["user_data"]
    summary = f"""
💼 Career Profile for {user.get('name', 'Student')}
- Career Goal: {user.get('career_goal', 'NA')}
- Internships Done: {user.get('internships_done', 'NA')}
- Job Ready: {user.get('job_ready', 'NA')}
- Suggested Paths: {user.get('suggested_paths', 'NA')}
"""
    prompt = build_agent_prompt("career_agent", summary, """
Assist by:
1. Recommending career options
2. Suggesting internships or certifications
3. Enhancing job readiness (resume/skills)
""")
    response = (prompt | llm).invoke({"question": state["question"], "prior": prior}).content
    full = summary + "\n---\n" + response
    state["messages"].append({"sender": "CareerAgent", "content": full})
    state["completed_agents"].append("career_agent")
    state["career_response"] = full
    log("career_agent", "Response generated", f"Response length: {len(response)} chars", state)
    return state

def wellness_agent(state: AgentState):
    prior = "\n".join([f"{m['sender']}: {m['content']}" for m in state["messages"]]) if state["messages"] else "No prior context"
    user = state["user_data"]
    summary = f"""
🧘 Wellness Profile for {user.get('name', 'Student')}
- Stress Level: {user.get('stress_level', 'NA')}
- Issues Reported: {user.get('issues_reported', 'NA')}
- Mental Health Support: {user.get('mental_health_support', 'NA')}
- Wellness Sessions: {user.get('wellness_sessions', 'NA')}
"""
    prompt = build_agent_prompt("wellness_agent", summary, """
Offer:
1. Stress management tips
2. Sleep hygiene advice
3. General wellness and self-care guidance
""")
    response = (prompt | llm).invoke({"question": state["question"], "prior": prior}).content
    full = summary + "\n---\n" + response
    state["messages"].append({"sender": "WellnessAgent", "content": full})
    state["completed_agents"].append("wellness_agent")
    state["wellness_response"] = full
    log("wellness_agent", "Response generated", f"Response length: {len(response)} chars", state)
    return state


# --- Workflow ---
def build_workflow(active_agents):
    graph = StateGraph(AgentState)
    for agent in active_agents:
        graph.add_node(agent, globals()[agent])
    def route_agents(state: AgentState):
        remaining = [a for a in active_agents if a not in state["completed_agents"]]
        return {"next": remaining[0]} if remaining else {"next": END}
    graph.add_node("route_agents", route_agents)
    for agent in active_agents:
        graph.add_edge(agent, "route_agents")
    graph.add_conditional_edges("route_agents", lambda s: s["next"], {a: a for a in active_agents} | {END: END})
    graph.set_entry_point(active_agents[0])
    return graph.compile()

# --- Streamlit UI ---
st.set_page_config("EduTrack LangGraph")
st.title("📚 EduTrack LangGraph")
q = st.text_input("Ask something:")

if q:
    start_time = time.time()
    state = {
        "question": q,
        "user_data": {},
        "messages": [],
        "completed_agents": [],
        "academic_response": "",
        "career_response": "",
        "wellness_response": "",
        "performance_response": "",
        "agent_log": [],
        "next": ""
    }

    state["user_data"] = extract_user_data(q, state)
    agents = detect_agents(q, state)
    if not agents:
        agents = ["academic_agent"]
    st.write("🧠 Activated Agents:", agents)

    flow = build_workflow(agents)
    result = flow.invoke(state)
    end_time = time.time()
    execution_time = end_time - start_time

    for msg in result["messages"]:
        st.markdown(f"**{msg['sender']}**\n\n{msg['content']}")

    st.subheader("✅ Completed Agents")
    for a in result["completed_agents"]:
        st.markdown(f"- {a}")

    st.subheader("📊 Execution Metrics")
    st.markdown(f"**🕒 Execution Time:** {execution_time:.2f} seconds")
    st.markdown(f"**🤖 Agents Invoked:** {', '.join(result['completed_agents'])}")
    st.markdown(f"**💬 No. of Communications:** {len(result['messages'])}")
    st.markdown(f"**🧾 Total Log Entries:** {len(result['agent_log'])}")

    st.subheader("🧠 Agent Flow Trace")
    emoji_map = {
        "router": "🧭",
        "data_context": "📁",
        "data_interpreter": "🔍",
        "selector": "🎯",
        "performance_agent": "📊",
        "academic_agent": "📘",
        "career_agent": "💼",
        "wellness_agent": "🧘",
        "system": "🛠️"
    }
    with st.expander("View Agent Flow Details"):
        for entry in result["agent_log"]:
            emoji = emoji_map.get(entry["agent"], "")
            st.markdown(f"""
- **[{entry['timestamp']}] {emoji} `{entry['agent'].upper()}`**
    - Action: {entry['action']}
    - Details: {entry['details']}
""")


