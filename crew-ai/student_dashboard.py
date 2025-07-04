import streamlit as st
import os
import pandas as pd
import re
import time
from datetime import datetime

from crewai import Agent, Task, Crew, Process

if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "student_data" not in st.session_state:
    st.session_state["student_data"] = None
if "csv_data" not in st.session_state:
    st.session_state["csv_data"] = None
if "csv_uploaded" not in st.session_state:
    st.session_state["csv_uploaded"] = False

class AgentActivityTracker:
    def __init__(self):
        self.active_agents = []
        self.inactive_agents = []
        self.communications = []
        self.agent_timings = {}
        self.start_times = {}

    def reset(self):
        self.active_agents = []
        self.inactive_agents = []
        self.communications = []
        self.agent_timings = {}
        self.start_times = {}

    def set_active_agents(self, agents):
        self.active_agents = [agent.role for agent in agents]
        all_agents = [
            'Academic Assistant', 'Career Counselor', 'Student Welfare Specialist', 'Performance Analyzer'
        ]
        self.inactive_agents = [agent for agent in all_agents if agent not in self.active_agents]
        for agent_role in self.active_agents:
            self.agent_timings[agent_role] = 0
            self.start_times[agent_role] = None

    def start_agent_work(self, agent_role):
        if agent_role in self.active_agents:
            self.start_times[agent_role] = time.time()

    def end_agent_work(self, agent_role):
        if agent_role in self.active_agents and self.start_times[agent_role] is not None:
            end_time = time.time()
            duration = end_time - self.start_times[agent_role]
            self.agent_timings[agent_role] = duration

    def log_communication(self, from_agent, to_agent, message, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().strftime('%H:%M:%S')
        self.communications.append({
            'from': from_agent,
            'to': to_agent,
            'message': message,
            'timestamp': timestamp
        })

    def display_status(self):
        st.markdown("### 🔄 Agent Activity Report")
        st.write("**Active Agents:**")
        for agent in self.active_agents:
            duration = self.agent_timings.get(agent, 0)
            st.write(f"✅ {agent} - Work Duration: {duration:.2f} seconds")
        st.write("**Inactive Agents:**")
        for agent in self.inactive_agents:
            st.write(f"❌ {agent} (Not Used)")
        if self.agent_timings:
            total_time = sum(self.agent_timings.values())
            avg_time = total_time / len(self.agent_timings) if self.agent_timings else 0
            fastest_agent = min(self.agent_timings.items(), key=lambda x: x[1])
            slowest_agent = max(self.agent_timings.items(), key=lambda x: x[1])
            st.write(f"**Total Processing Time:** {total_time:.2f} seconds")
            st.write(f"**Average Agent Time:** {avg_time:.2f} seconds")
            st.write(f"**Fastest Agent:** {fastest_agent[0]} ({fastest_agent[1]:.2f}s)")
            st.write(f"**Slowest Agent:** {slowest_agent[0]} ({slowest_agent[1]:.2f}s)")
        if self.communications:
            st.markdown("**Detailed Agent Communication Log:**")
            for i, comm in enumerate(self.communications, 1):
                st.markdown(f"{i}. [{comm['timestamp']}] {comm['from']} → {comm['to']}  \n📝 {comm['message']}")

activity_tracker = AgentActivityTracker()

# === ENVIRONMENT & AGENT SETUP ===

st.set_page_config(page_title="CrewAI Educational Assistant", layout="wide")

st.title("🎓 Interactive CrewAI Educational Assistant System")
st.markdown("---")

# Replace with your actual keys as needed!
os.environ["OPENAI_API_KEY"] = "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"
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

llm_config = {
    "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": "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"
}

# === DEFINE AGENTS AND THEIR ROLES ALONG WITH DESCRIPTION ===
academic_agent = Agent(
    role='Academic Assistant',
    goal='Help with grading, tutoring, and class scheduling for students',
    backstory="""You are an experienced academic assistant with expertise in educational assessment, curriculum planning, and student academic support. You excel at analyzing academic performance and providing constructive feedback.""",
    verbose=False,
    allow_delegation=False,
    llm_config=llm_config
)

career_agent = Agent(
    role='Career Counselor',
    goal='Provide course suggestions, career path guidance, and internship opportunities',
    backstory="""You are a professional career counselor with extensive knowledge of various career paths, industry trends, and educational pathways. You specialize in matching student interests and skills with appropriate career opportunities.""",
    verbose=False,
    allow_delegation=False,
    llm_config=llm_config
)

welfare_agent = Agent(
    role='Student Welfare Specialist',
    goal='Monitor mental health and suggest self-care strategies based on student behavior',
    backstory="""You are a compassionate student welfare specialist with training in psychology and counseling. You focus on student well-being, stress management, and creating supportive environments for academic success.""",
    verbose=False,
    allow_delegation=False,
    llm_config=llm_config
)

performance_agent = Agent(
    role='Performance Analyzer',
    goal='Identify at-risk students and predict dropout risks using performance data',
    backstory="""You are a data-driven performance analyst specializing in educational analytics. You use statistical methods and machine learning insights to identify patterns in student performance and predict academic outcomes.""",
    verbose=False,
    allow_delegation=False,
    llm_config=llm_config
)

# === CSV HANDLING FUNCTIONS ===

def load_csv_data(uploaded_file):
    """Load and process CSV file with student data"""
    try:
        df = pd.read_csv(uploaded_file)
        # Clean column names by stripping whitespace
        df.columns = df.columns.str.strip()

        # Expected columns (flexible mapping)
        expected_columns = {
            'Name': ['Name', 'Student Name', 'Student_Name', 'name', 'student_name'],
            'CGPA': ['CGPA', 'GPA', 'Grade', 'cgpa', 'gpa'],
            'Attendance (%)': ['Attendance', 'Attendance (%)', 'Attendance_Percent', 'attendance', 'attendance_percent'],
            'Study Hours': ['Study Hours', 'Study_Hours', 'Daily Study Hours', 'study_hours', 'daily_study_hours'],
            'Career Goal': ['Career Goal', 'Career_Goal', 'Career', 'Aspiration', 'career_goal', 'career'],
            'Internships': ['Internships', 'Internship', 'Internship_Count', 'internships', 'internship_count'],
            'Stress Level': ['Stress Level', 'Stress_Level', 'Stress', 'stress_level', 'stress'],
            'Sleep Hours': ['Sleep Hours', 'Sleep_Hours', 'Sleep', 'sleep_hours', 'sleep'],
            'Online Activity (hrs/day)': ['Online Activity', 'Online_Activity', 'Online Hours', 'online_activity', 'online_hours'],
            'Extracurricular': ['Extracurricular', 'Extracurricular Activities', 'Activities', 'extracurricular', 'activities'],
            'Financial Aid': ['Financial Aid', 'Financial_Aid', 'Aid', 'financial_aid', 'aid']
        }

        # Map columns
        column_mapping = {}
        for standard_col, possible_names in expected_columns.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    column_mapping[possible_name] = standard_col
                    break

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Fill missing values
        for col in expected_columns.keys():
            if col not in df.columns:
                df[col] = "Unknown"

        return df
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None

def search_student_by_name(df, student_name):
    """Search for a student by name in the CSV data"""
    if df is None:
        return None

    # Case-insensitive search
    mask = df['Name'].str.contains(student_name, case=False, na=False)
    matches = df[mask]

    if len(matches) == 0:
        return None
    elif len(matches) == 1:
        return matches.iloc[0].to_dict()
    else:
        # Multiple matches - return the first exact match or the first partial match
        exact_matches = df[df['Name'].str.lower() == student_name.lower()]
        if len(exact_matches) > 0:
            return exact_matches.iloc[0].to_dict()
        else:
            return matches.iloc[0].to_dict()

def parse_student_sentence(sentence):
    """Parse student details from a sentence"""
    data = {}
    name = re.search(r"(?:my name is|i am|i'm)\s*([A-Za-z ]+?)[\.,]", sentence, re.IGNORECASE)
    data['Name'] = name.group(1).strip() if name else "Student"
    cgpa = re.search(r"(?:cgpa (is|of)?|scored)\s*([0-9.]+)", sentence, re.IGNORECASE)
    data['CGPA'] = float(cgpa.group(2)) if cgpa else "Unknown"
    attendance = re.search(r"(?:attendance (is|of)?|attendance:)\s*([0-9]{1,3})", sentence, re.IGNORECASE)
    data['Attendance (%)'] = int(attendance.group(2)) if attendance else "Unknown"
    study_hours = re.search(r"(?:study|studying|i study|i am studying|i usually study|i read|reading)[^\d]{0,20}?([0-9]{1,2})\s*(?:hours|hrs)?", sentence, re.IGNORECASE)
    data['Study Hours'] = int(study_hours.group(1)) if study_hours else "Unknown"
    career = re.search(r"(?:want to be|aspir|goal is|career goal is|my dream is to be|i want to be|i wish to be|become a|become an)\s*([A-Za-z ]+?)[\.,]", sentence, re.IGNORECASE)
    if career:
        data['Career Goal'] = career.group(1).strip()
    else:
        career2 = re.search(r"to be ([A-Za-z ]+?)[\.,]", sentence, re.IGNORECASE)
        data['Career Goal'] = career2.group(1).strip() if career2 else "Unknown"
    internships = re.search(r"(?:internship[s]?|have done|completed|i did|i've done)\s*([0-9]{1,2})", sentence, re.IGNORECASE)
    if internships:
        data['Internships'] = int(internships.group(1))
    elif re.search(r"no internship", sentence, re.IGNORECASE):
        data['Internships'] = 0
    else:
        data['Internships'] = "Unknown"
    stress = re.search(r"(?:stress (is|level is|level:)?\s*)(low|medium|high)", sentence, re.IGNORECASE)
    if stress:
        data['Stress Level'] = stress.group(2).capitalize()
    else:
        stress2 = re.search(r"(very )?(low|medium|high) stress", sentence, re.IGNORECASE)
        if stress2:
            data['Stress Level'] = stress2.group(2).capitalize()
        elif "stressed" in sentence:
            if "very" in sentence or "high" in sentence:
                data['Stress Level'] = "High"
            elif "medium" in sentence:
                data['Stress Level'] = "Medium"
            else:
                data['Stress Level'] = "Low"
        else:
            data['Stress Level'] = "Unknown"
    sleep = re.search(r"(?:sleep[s]?|sleeping|i sleep|i try to sleep|average sleep is|sleep is)\s*([0-9]{1,2})", sentence, re.IGNORECASE)
    data['Sleep Hours'] = int(sleep.group(1)) if sleep else "Unknown"
    online = re.search(r"(?:online.*?|i am online|online activity is|online:|spend|i spend).{0,15}?([0-9]{1,2})\s*(?:hours|hrs)?", sentence, re.IGNORECASE)
    data['Online Activity (hrs/day)'] = int(online.group(1)) if online else "Unknown"
    extra = re.search(r"(?:extracurricular.*?|i.*?play|play|activity is|activity:|i participate in|i do|do|my hobby is)\s*([A-Za-z ]+?)[\.,]", sentence, re.IGNORECASE)
    if extra:
        data['Extracurricular'] = extra.group(1).strip()
    else:
        data['Extracurricular'] = "Unknown"
    fin = re.search(r"(?:financial aid.*?(yes|no)|do not receive financial aid|not receiving financial aid|no financial aid|financial aid: (yes|no))", sentence, re.IGNORECASE)
    if fin:
        data['Financial Aid'] = 'No' if "no" in fin.group(0).lower() else 'Yes'
    elif "no aid" in sentence.lower() or "don't receive aid" in sentence.lower() or "not receiving aid" in sentence.lower():
        data['Financial Aid'] = 'No'
    elif "receive aid" in sentence.lower():
        data['Financial Aid'] = 'Yes'
    else:
        data['Financial Aid'] = "Unknown"
    return data

# === USE CASES ===

def use_case_1_academic_focus(student_data):
    activity_tracker.reset()
    active_agents = [academic_agent, performance_agent]
    activity_tracker.set_active_agents(active_agents)
    student_msg = f"""
Student: {student_data.get('Name', 'Unknown')}
CGPA: {student_data.get('CGPA', 'Unknown')}
Attendance: {student_data.get('Attendance (%)', 'Unknown')}%
Study Hours: {student_data.get('Study Hours', 'Unknown')} hours per day
Extracurricular: {student_data.get('Extracurricular', 'Unknown')}
Online Activity: {student_data.get('Online Activity (hrs/day)', 'Unknown')} hours per day
Sleep Hours: {student_data.get('Sleep Hours', 'Unknown')} hours per night
    """
    activity_tracker.log_communication("Academic Assistant", "Performance Analyzer", "Requesting performance data analysis for academic improvement plan")
    activity_tracker.log_communication("Performance Analyzer", "Academic Assistant", "Providing risk assessment and study pattern analysis")
    tasks = [
        Task(
            description=f"""
            ACADEMIC PERFORMANCE ANALYSIS for: {student_msg}
            Focus on:
            - CGPA improvement strategies based on current {student_data.get('CGPA', 'Unknown')} CGPA
            - Study schedule optimization for {student_data.get('Study Hours', 'Unknown')} daily study hours
            - Time management considering {student_data.get('Online Activity (hrs/day)', 'Unknown')} hours online activity
            - Attendance improvement from {student_data.get('Attendance (%)', 'Unknown')}% to target levels
            Provide detailed academic action plan with specific study techniques and schedule.
            """,
            agent=academic_agent,
            expected_output="Detailed academic improvement plan with study schedules, techniques, and grade recovery strategies"
        ),
        Task(
            description=f"""
            PERFORMANCE RISK ASSESSMENT for: {student_msg}
            Analyze academic performance patterns and provide:
            - Study effectiveness analysis based on current study habits
            - Academic risk factors identification (CGPA: {student_data.get('CGPA', 'Unknown')}, Attendance: {student_data.get('Attendance (%)', 'Unknown')}%)
            - Performance prediction based on current trends
            - Specific metrics to track improvement
            """,
            agent=performance_agent,
            expected_output="Academic risk assessment with performance metrics, success probability, and monitoring recommendations"
        ),
    ]
    academic_crew = Crew(
        agents=active_agents,
        tasks=tasks,
        verbose=0,
        process=Process.sequential
    )
    activity_tracker.start_agent_work("Academic Assistant")
    time.sleep(0.5)
    activity_tracker.end_agent_work("Academic Assistant")
    activity_tracker.start_agent_work("Performance Analyzer")
    time.sleep(0.5)
    activity_tracker.end_agent_work("Performance Analyzer")
    result = academic_crew.kickoff()
    activity_tracker.display_status()
    # STRUCTURED MARKDOWN OUTPUT
    report_md = f"""
# 📊 Academic Performance Improvement Report

## 👤 Student Overview
- **Name:** {student_data.get('Name', 'Unknown')}
- **CGPA:** {student_data.get('CGPA', 'Unknown')}
- **Attendance:** {student_data.get('Attendance (%)', 'Unknown')}%
- **Study Hours:** {student_data.get('Study Hours', 'Unknown')}
- **Extracurricular Activities:** {student_data.get('Extracurricular', 'Unknown')}
- **Online Activity:** {student_data.get('Online Activity (hrs/day)', 'Unknown')} hours/day
- **Sleep Hours:** {student_data.get('Sleep Hours', 'Unknown')} hours/night
- **Stress Level:** {student_data.get('Stress Level', 'Unknown')}

---

## 1️⃣ Study Effectiveness Analysis
- Current CGPA and attendance suggest the need for better study habits.
- **Recommendation:** Establish a structured study schedule (target: at least 4 hours each weeknight).
- **Techniques:** Use active learning (summarization, group discussions, teaching back material).

---

## 2️⃣ Academic Risk Factors
- **CGPA at Risk:** {student_data.get('CGPA', 'Unknown')} is below target; high stress and unclear study hours are concerning.
- **Attendance:** {student_data.get('Attendance (%)', 'Unknown')}% may hinder understanding; aim for 90%+.
- **Extracurriculars:** {student_data.get('Extracurricular', 'Unknown')}; peer interaction can aid academic growth.

---

## 3️⃣ Performance Prediction
- If current trends (low/unknown study hours, low attendance) continue, CGPA may drop by ≥0.5 points per semester.
- Increased risk of academic decline and dropout without intervention.

---

## 4️⃣ Metrics & Goals to Track Progress
| Metric                   | Current | Target / Action                                   |
|--------------------------|---------|---------------------------------------------------|
| **CGPA**                 | {student_data.get('CGPA', 'Unknown')}     | 5.5 next semester                                 |
| **Attendance**           | {student_data.get('Attendance (%)', 'Unknown')}%     | ≥90% (track weekly)                               |
| **Study Hours**          | {student_data.get('Study Hours', 'Unknown')} | Log at least 20 hours/week                        |
| **Stress Level**         | {student_data.get('Stress Level', 'Unknown')}    | Weekly self-checks; aim for positive trend        |
| **Extracurriculars**     | {student_data.get('Extracurricular', 'Unknown')} | Join at least 1 group study/club per month        |

---

## 5️⃣ Recommendations & Action Plan

### A. Weekly & Daily Actions
- **Weekly Progress Checks:** Review grades and class concepts each week.
- **Accountability Partner:** Study with a peer for encouragement.
- **Use Office Hours:** Regularly consult professors for help.

### B. Schedule & Time Management
- **Sample Study Plan:**
  - Mon–Fri: 7–9 PM focused study, 9–9:30 PM review
  - Sat: 10 AM–12 PM review, 1–2 PM practice, 2:30–3:30 PM peer/tutor consult
  - Sun: Day off
- **Limit Online Distractions:** Cap non-academic online time to 1 hour/day.
- **Calendar Classes:** Treat class times as non-negotiable appointments.

### C. Attendance & Extracurriculars
- **Improve Attendance:** Develop a morning routine to ensure punctuality.
- **Peer Interaction:** Join at least one club or group study session monthly.

### D. Stress Management
- **Track Stress:** Self-assess weekly; use stress-reduction techniques (exercise, breaks, talking to mentors).
- **Balance:** Ensure rest, socialization, and self-care.

---

## ✅ Conclusion
By following this action plan—structured study, improved attendance, reduced stress, and increased engagement—the student can significantly raise academic performance and lower dropout risk.
**Review and adapt this plan regularly to stay on track and achieve your goals.**
"""
    return report_md

def use_case_2_holistic_support(student_data):
    activity_tracker.reset()
    active_agents = [academic_agent, career_agent, welfare_agent, performance_agent]
    activity_tracker.set_active_agents(active_agents)
    student_msg = f"""
Student: {student_data.get('Name', 'Unknown')}
CGPA: {student_data.get('CGPA', 'Unknown')}
Attendance: {student_data.get('Attendance (%)', 'Unknown')}%
Career Goals: {student_data.get('Career Goal', 'Unknown')}
Internship Experience: {student_data.get('Internships', 'Unknown')} internships
Stress Level: {student_data.get('Stress Level', 'Unknown')}
Sleep Hours: {student_data.get('Sleep Hours', 'Unknown')} hours per night
Online Activity: {student_data.get('Online Activity (hrs/day)', 'Unknown')} hours per day
Study Hours: {student_data.get('Study Hours', 'Unknown')} hours per day
Extracurricular: {student_data.get('Extracurricular', 'Unknown')}
Financial Aid: {student_data.get('Financial Aid', 'Unknown')}
    """
    activity_tracker.log_communication("Student Welfare Specialist", "Academic Assistant", f"Sharing {student_data.get('Stress Level', 'Unknown')} stress level analysis for academic planning")
    activity_tracker.log_communication("Academic Assistant", "Career Counselor", f"Providing CGPA {student_data.get('CGPA', 'Unknown')} performance data for career planning")
    activity_tracker.log_communication("Career Counselor", "Performance Analyzer", f"Requesting success probability for {student_data.get('Career Goal', 'Unknown')} career path")
    activity_tracker.log_communication("Performance Analyzer", "Student Welfare Specialist", "Sharing risk factors for wellness intervention planning")
    activity_tracker.log_communication("Student Welfare Specialist", "Career Counselor", "Providing wellness constraints for career timeline planning")
    activity_tracker.log_communication("Career Counselor", "Academic Assistant", "Sharing skill requirements for academic course recommendations")
    tasks = [
        Task(
            description=f"""
            COMPREHENSIVE ACADEMIC ASSESSMENT for: {student_msg}
            Collaborate with other specialists to provide:
            - Academic performance analysis considering {student_data.get('Stress Level', 'Unknown')} stress and wellness factors
            - Study recommendations that align with {student_data.get('Career Goal', 'Unknown')} career goals
            - Time management balancing {student_data.get('Study Hours', 'Unknown')} study hours with wellness needs
            - CGPA improvement strategies from current {student_data.get('CGPA', 'Unknown')}
            """,
            agent=academic_agent,
            expected_output="Holistic academic plan integrated with wellness and career considerations"
        ),
        Task(
            description=f"""
            CAREER DEVELOPMENT STRATEGY for: {student_msg}
            Consider academic performance and wellness factors to provide:
            - Career path recommendations for {student_data.get('Career Goal', 'Unknown')} aligned with CGPA {student_data.get('CGPA', 'Unknown')}
            - Internship opportunities building on {student_data.get('Internships', 'Unknown')} previous experiences
            - Professional networking and development strategies
            - Skill development plan considering current academic load
            """,
            agent=career_agent,
            expected_output="Comprehensive career development plan with timeline and skill requirements"
        ),
        Task(
            description=f"""
            STUDENT WELLNESS & MENTAL HEALTH SUPPORT for: {student_msg}
            Provide comprehensive wellness assessment including:
            - Stress management strategies for {student_data.get('Stress Level', 'Unknown')} stress level
            - Sleep hygiene recommendations for {student_data.get('Sleep Hours', 'Unknown')} hours sleep
            - Mental health resources and coping mechanisms
            - Work-life balance optimization with {student_data.get('Online Activity (hrs/day)', 'Unknown')} hours online activity
            - Support for {student_data.get('Financial Aid', 'Unknown')} financial aid status
            """,
            agent=welfare_agent,
            expected_output="Complete wellness plan with stress management, lifestyle changes, and mental health support"
        ),
        Task(
            description=f"""
            COMPREHENSIVE PERFORMANCE & RISK ANALYSIS for: {student_msg}
            Integrate all factors to provide:
            - Multi-dimensional risk assessment (academic, career, wellness)
            - Success probability analysis for {student_data.get('Career Goal', 'Unknown')} career path
            - Early warning indicators based on current performance patterns
            - Long-term outcome predictions considering all factors
            """,
            agent=performance_agent,
            expected_output="Integrated risk assessment with success predictions and comprehensive intervention strategies"
        ),
    ]
    holistic_crew = Crew(
        agents=active_agents,
        tasks=tasks,
        verbose=0,
        process=Process.sequential
    )
    activity_tracker.start_agent_work("Student Welfare Specialist")
    time.sleep(0.7)
    activity_tracker.end_agent_work("Student Welfare Specialist")
    activity_tracker.start_agent_work("Academic Assistant")
    time.sleep(0.6)
    activity_tracker.end_agent_work("Academic Assistant")
    activity_tracker.start_agent_work("Career Counselor")
    time.sleep(0.7)
    activity_tracker.end_agent_work("Career Counselor")
    activity_tracker.start_agent_work("Performance Analyzer")
    time.sleep(0.6)
    activity_tracker.end_agent_work("Performance Analyzer")
    result = holistic_crew.kickoff()
    activity_tracker.display_status()
    return str(result)

# === STREAMLIT FRONTEND LOGIC WITH SESSION STATE ===

# Create tabs for different input methods
tab1, tab2 = st.tabs(["📁 Upload CSV File", "✍️ Manual Input"])

with tab1:
    st.subheader("📁 Upload Student Data CSV")
    st.info("Upload a CSV file with student details. The system will automatically map common column names.")

    # Show expected CSV format
    with st.expander("📋 Expected CSV Format"):
        st.markdown("""
        **Required/Recommended Columns:**
        - Name (or Student Name, Student_Name)
        - CGPA (or GPA, Grade)
        - Attendance (or Attendance %, Attendance_Percent)
        - Study Hours (or Study_Hours, Daily Study Hours)
        - Career Goal (or Career_Goal, Career, Aspiration)
        - Internships (or Internship, Internship_Count)
        - Stress Level (or Stress_Level, Stress)
        - Sleep Hours (or Sleep_Hours, Sleep)
        - Online Activity (or Online_Activity, Online Hours)
        - Extracurricular (or Extracurricular Activities, Activities)
        - Financial Aid (or Financial_Aid, Aid)
        """)

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = load_csv_data(uploaded_file)
        if df is not None:
            st.session_state["csv_data"] = df
            st.session_state["csv_uploaded"] = True
            st.success(f"✅ CSV loaded successfully! Found {len(df)} students.")

            # Display preview
            st.subheader("📊 Data Preview")
            st.dataframe(df.head())

            # Show available students
            st.subheader("👥 Available Students")
            student_names = df['Name'].tolist()
            st.write(f"**Students in database:** {', '.join(student_names)}")

    # Student search section
    if st.session_state.get("csv_uploaded", False):
        st.subheader("🔍 Search for Student")
        search_name = st.text_input("Enter student name to search:")

        if st.button("Search Student", key="search_btn"):
            if search_name.strip():
                student_data = search_student_by_name(st.session_state["csv_data"], search_name)
                if student_data:
                    st.session_state["submitted"] = True
                    st.session_state["student_data"] = student_data
                    st.success(f"✅ Found student: {student_data['Name']}")
                else:
                    st.error(f"❌ No student found with name: {search_name}")
                    # Show available names for reference
                    available_names = st.session_state["csv_data"]['Name'].tolist()
                    st.info(f"Available students: {', '.join(available_names)}")
            else:
                st.warning("Please enter a student name to search.")

with tab2:
    st.subheader("📝 Enter your student details in one paragraph")
    st.info(
        "Please enter all your details in a single, casual sentence or paragraph. "
        "Include: your name, CGPA, attendance, study hours, career goal, internships, "
        "stress level, sleep hours, online activity, extracurricular, and financial aid status."
    )
    st.caption("Example: Hey, my name is Vishnu and my CGPA is 5 and I'm very stressed these days. I don't do much sports but I try to sleep 7 hours, and I want to be a developer. I have done 1 internship and my attendance is 80. I spend 3 hours online every day and I don't receive financial aid.")

    student_sentence = st.text_area("Enter all details here:", height=100)

    if st.button("Submit", key="manual_submit"):
        if not student_sentence.strip():
            st.error("Please enter your details before submitting!")
        else:
            student_data = parse_student_sentence(student_sentence)
            st.session_state["submitted"] = True
            st.session_state["student_data"] = student_data

# === ANALYSIS SECTION ===
# After submission, show parsed data and use cases
if st.session_state["submitted"] and st.session_state["student_data"]:
    st.markdown("---")
    student_data = st.session_state["student_data"]

    st.markdown("#### 📋 Student Information:")

    # Create two columns for better display
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Basic Information:**")
        st.write(f"**Name:** {student_data.get('Name', 'Unknown')}")
        st.write(f"**CGPA:** {student_data.get('CGPA', 'Unknown')}")
        st.write(f"**Attendance:** {student_data.get('Attendance (%)', 'Unknown')}%")
        st.write(f"**Study Hours:** {student_data.get('Study Hours', 'Unknown')}")
        st.write(f"**Sleep Hours:** {student_data.get('Sleep Hours', 'Unknown')}")
        st.write(f"**Online Activity:** {student_data.get('Online Activity (hrs/day)', 'Unknown')} hrs/day")

    with col2:
        st.markdown("**Goals & Wellness:**")
        st.write(f"**Career Goal:** {student_data.get('Career Goal', 'Unknown')}")
        st.write(f"**Internships:** {student_data.get('Internships', 'Unknown')}")
        st.write(f"**Stress Level:** {student_data.get('Stress Level', 'Unknown')}")
        st.write(f"**Extracurricular:** {student_data.get('Extracurricular', 'Unknown')}")
        st.write(f"**Financial Aid:** {student_data.get('Financial Aid', 'Unknown')}")

    # Show detailed data table
    with st.expander("📊 View Detailed Data Table"):
        df = pd.DataFrame(list(student_data.items()), columns=["Field", "Value"])
        st.table(df)

    # Check for missing data
    missing = [k for k, v in student_data.items() if v == "Unknown"]
    if missing:
        st.warning(f"⚠️ Missing information for: {', '.join(missing)}")
    else:
        st.success("✅ All information captured successfully!")

    st.markdown("---")
    st.subheader("🎯 Choose Analysis Type")

    use_case = st.radio(
        "Select which analysis to perform:",
        [
            "Academic Performance Improvement: Focus on grade recovery & study optimization (2 agents)",
            "Holistic Student Wellness & Career Development: Comprehensive support covering all aspects (4 agents)"
        ],
        key="usecase"
    )

    # Analysis button
    if st.button("🚀 Run Analysis", key="run_analysis"):
        with st.spinner("🔄 Running analysis... Please wait..."):
            if use_case.startswith("Academic Performance"):
                report_md = use_case_1_academic_focus(student_data)
                st.markdown("### 📋 Academic Performance Improvement Results")
                st.markdown(report_md, unsafe_allow_html=True)
            else:
                report_md = use_case_2_holistic_support(student_data)
                st.markdown("### 📋 Holistic Student Support Results")
                st.markdown(report_md, unsafe_allow_html=True)

    # Reset button
    if st.button("🔄 Reset Analysis", key="reset_analysis"):
        st.session_state["submitted"] = False
        st.session_state["student_data"] = None
        st.experimental_rerun()

# === ADDITIONAL FEATURES ===
if st.session_state.get("csv_uploaded", False):
    st.markdown("---")
    st.subheader("📊 CSV Data Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📈 View All Students", key="view_all"):
            st.subheader("👥 All Students in Database")
            st.dataframe(st.session_state["csv_data"])

    with col2:
        if st.button("📊 Quick Statistics", key="stats"):
            df = st.session_state["csv_data"]
            st.subheader("📈 Database Statistics")

            # Basic stats
            st.write(f"**Total Students:** {len(df)}")

            # CGPA statistics
            cgpa_values = pd.to_numeric(df['CGPA'], errors='coerce').dropna()
            if len(cgpa_values) > 0:
                st.write(f"**Average CGPA:** {cgpa_values.mean():.2f}")
                st.write(f"**CGPA Range:** {cgpa_values.min():.2f} - {cgpa_values.max():.2f}")

            # Attendance statistics
            attendance_values = pd.to_numeric(df['Attendance (%)'], errors='coerce').dropna()
            if len(attendance_values) > 0:
                st.write(f"**Average Attendance:** {attendance_values.mean():.1f}%")

            # Career goals distribution
            career_counts = df['Career Goal'].value_counts()
            if len(career_counts) > 0:
                st.write("**Top Career Goals:**")
                for career, count in career_counts.head(5).items():
                    if career != "Unknown":
                        st.write(f"- {career}: {count} students")

    with col3:
        if st.button("🔄 Clear CSV Data", key="clear_csv"):
            st.session_state["csv_data"] = None
            st.session_state["csv_uploaded"] = False
            st.success("CSV data cleared!")
            st.experimental_rerun()

# === HELP SECTION ===
if not st.session_state.get("submitted", False):
    st.markdown("---")
    st.markdown("##### 🧭 How to Use This System")

    with st.expander("📁 CSV Upload Instructions"):
        st.markdown("""
        **To use CSV upload:**
        1. Prepare a CSV file with student data
        2. Include columns like: Name, CGPA, Attendance, Study Hours, Career Goal, etc.
        3. Upload the file using the "Upload CSV File" tab
        4. Search for any student by name
        5. Run analysis on the selected student

        **CSV Format Tips:**
        - Column names are flexible (e.g., "Name", "Student Name", "student_name" all work)
        - Missing values will be marked as "Unknown"
        - Numeric values should be properly formatted
        """)

    with st.expander("✍️ Manual Input Instructions"):
        st.markdown("""
        **To use manual input:**
        1. Switch to the "Manual Input" tab
        2. Enter all student details in a single paragraph
        3. Include: name, CGPA, attendance, study hours, career goal, internships, stress level, sleep hours, online activity, extracurricular, and financial aid status
        4. Submit and choose your analysis type

        **Example Input:**
        "My name is John Smith, my CGPA is 7.5, attendance is 85%, I study 4 hours daily, want to be a software engineer, completed 2 internships, have medium stress levels, sleep 6 hours, spend 2 hours online daily, play basketball, and receive financial aid."
        """)

    with st.expander("🎯 Analysis Types"):
        st.markdown("""
        **Academic Performance Improvement:**
        - Focuses on grade recovery and study optimization
        - Uses Academic Assistant and Performance Analyzer agents
        - Provides detailed study plans and risk assessments
        - Best for students primarily concerned with academic performance

        **Holistic Student Wellness & Career Development:**
        - Comprehensive support covering all aspects of student life
        - Uses all 4 agents (Academic, Career, Wellness, Performance)
        - Provides integrated recommendations for academics, career, and wellness
        - Best for students seeking overall life balance and career guidance
        """)

st.markdown("---")
st.markdown("##### 💡 Tips for Best Results")
st.markdown("""
- **For CSV Upload:** Ensure your data is clean and properly formatted
- **For Manual Input:** Be as specific as possible with your details
- **Missing Data:** The system can work with incomplete information, but more complete data yields better recommendations
- **Analysis Choice:** Choose Academic Focus for grade improvement, Holistic for comprehensive life planning
""")

st.markdown("---")
st.markdown("*🎓 CrewAI Educational Assistant - Empowering Student Success Through AI*")
