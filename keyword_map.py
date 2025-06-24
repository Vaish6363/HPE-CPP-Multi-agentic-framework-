from agents import academic, career, welfare, performance

# ACADEMIC KEYWORDS (300 total)
academic_keywords = [
    # Core Academic Terms
    "academic", "academics", "education", "educational", "learning", "study", "studying", "studies",
    "school", "college", "university", "curriculum", "syllabus", "course", "courses", "subject", "subjects",
    "class", "classes", "lecture", "lectures", "tutorial", "tutorials", "seminar", "seminars",
    
    # Grades and Assessment
    "grade", "grades", "grading", "gpa", "cgpa", "marks", "score", "scores", "scoring", "result", "results",
    "exam", "exams", "examination", "test", "tests", "testing", "quiz", "quizzes", "assessment", "assessments",
    "midterm", "finals", "final exam", "evaluation", "feedback", "report card", "transcript", "diploma",
    
    # Study Methods and Skills
    "homework", "assignment", "assignments", "project", "projects", "research", "thesis", "dissertation",
    "essay", "essays", "paper", "papers", "report", "reports", "presentation", "presentations",
    "note", "notes", "note-taking", "notebook", "textbook", "textbooks", "reading", "revision",
    "practice", "exercise", "exercises", "problem", "problems", "solution", "solutions",
    
    # STEM Subjects
    "mathematics", "math", "maths", "algebra", "geometry", "calculus", "statistics", "probability",
    "physics", "chemistry", "biology", "science", "sciences", "engineering", "technology",
    "computer science", "programming", "coding", "software", "hardware", "algorithms", "data structures",
    "dsa", "competitive programming", "machine learning", "artificial intelligence", "ai", "ml",
    
    # Liberal Arts
    "english", "literature", "writing", "grammar", "vocabulary", "history", "geography", "social studies",
    "psychology", "sociology", "philosophy", "economics", "political science", "linguistics",
    "anthropology", "art", "music", "drama", "theater", "dance",
    
    # Academic Challenges
    "difficult", "difficulty", "hard", "challenging", "struggle", "struggling", "confused", "confusion",
    "understand", "understanding", "comprehension", "concept", "concepts", "theory", "theories",
    "weak", "weakness", "strength", "strengths", "gap", "gaps", "knowledge gap",
    
    # Academic Support
    "tutor", "tutoring", "mentor", "mentoring", "teacher", "professor", "instructor", "faculty",
    "study group", "peer support", "collaboration", "discussion", "doubt", "doubts", "clarification",
    "help", "assistance", "guidance", "advice", "tips", "strategies", "techniques",
    
    # Time Management
    "schedule", "timetable", "deadline", "deadlines", "due date", "submission", "time management",
    "study plan", "study schedule", "planning", "organization", "productivity", "efficiency",
    "procrastination", "distraction", "distractions", "focus", "concentration", "attention",
    
    # Academic Goals
    "goal", "goals", "target", "targets", "objective", "objectives", "aim", "aims", "ambition",
    "scholarship", "honor", "honors", "award", "awards", "recognition", "achievement",
    "success", "successful", "excellence", "distinction", "merit", "ranking", "rank"
]

# CAREER KEYWORDS (300 total)  
career_keywords = [
    # Core Career Terms
    "career", "careers", "job", "jobs", "work", "working", "employment", "profession", "professional",
    "occupation", "vocation", "field", "industry", "sector", "position", "role", "title",
    
    # Job Search
    "job search", "job hunting", "apply", "application", "applications", "resume", "cv", "curriculum vitae",
    "cover letter", "portfolio", "interview", "interviews", "interviewing", "job interview",
    "hiring", "recruitment", "recruiter", "hr", "human resources", "placement",
    
    # Technology Careers
    "software developer", "programmer", "coding", "web developer", "app developer", "full stack",
    "frontend", "backend", "data scientist", "data analyst", "data engineer", "machine learning engineer",
    "ai engineer", "cybersecurity", "network engineer", "system administrator", "devops",
    "product manager", "project manager", "tech lead", "architect",
    
    # Business Careers
    "business analyst", "consultant", "consulting", "management", "manager", "executive",
    "entrepreneur", "startup", "business development", "sales", "marketing", "digital marketing",
    "finance", "accounting", "investment banking", "financial analyst", "operations",
    
    # Healthcare Careers
    "doctor", "physician", "nurse", "healthcare", "medical", "dentist", "pharmacist",
    "therapist", "physiotherapist", "psychologist", "psychiatrist", "surgeon",
    
    # Education Careers
    "teacher", "educator", "professor", "academic", "researcher", "principal", "administrator",
    "curriculum designer", "instructional designer", "trainer", "coach", "mentor", "tutor",
    
    # Creative Careers
    "designer", "graphic designer", "web designer", "ux designer", "ui designer", "artist",
    "writer", "content writer", "copywriter", "journalist", "editor", "photographer",
    "videographer", "filmmaker", "animator", "musician", "actor", "director",
    
    # Career Development
    "career development", "career growth", "advancement", "promotion", "career path", "career planning",
    "professional development", "skill development", "upskilling", "reskilling", "training",
    "certification", "certifications", "workshop", "workshops", "seminar",
    
    # Work Environment
    "office", "remote work", "work from home", "hybrid", "freelance", "freelancer", "contractor",
    "consultant", "part-time", "full-time", "internship", "apprenticeship", "temporary",
    "permanent", "contract", "gig", "startup", "corporate", "government",
    
    # Career Skills
    "skills", "hard skills", "soft skills", "technical skills", "communication skills",
    "leadership", "management", "teamwork", "collaboration", "problem solving", "analytical",
    "creative", "innovative", "adaptable", "flexible", "reliable", "organized",
    
    # Salary and Benefits
    "salary", "wage", "pay", "compensation", "benefits", "package", "bonus", "incentive",
    "raise", "increment", "negotiation", "equity", "stock options", "retirement",
    "insurance", "healthcare", "vacation", "perks",
    
    # Networking
    "networking", "network", "connections", "contacts", "relationships", "mentor", "mentorship",
    "colleague", "peer", "professional association", "conference", "linkedin", "referral",
    
    # Career Challenges
    "unemployment", "layoff", "fired", "terminated", "job loss", "career crisis", "stuck",
    "plateau", "burnout", "stress", "competition", "rejection", "setback", "challenge",
    
    # Career Success
    "promotion", "advancement", "recognition", "award", "achievement", "success", "excellence",
    "leadership role", "senior position", "executive", "director", "expert", "specialist"
]

# PERFORMANCE KEYWORDS (300 total)
performance_keywords = [
    # Core Performance Terms
    "performance", "improve", "improvement", "better", "best", "enhance", "enhancement", "optimize",
    "optimization", "progress", "progression", "development", "growth", "advancement", "upgrade",
    "boost", "increase", "maximize", "excel", "excellence", "achieve", "achievement", "accomplish",
    
    # Performance Measurement
    "measure", "measurement", "metric", "metrics", "kpi", "indicator", "benchmark", "standard",
    "goal", "goals", "target", "targets", "objective", "objectives", "result", "results",
    "outcome", "output", "productivity", "efficiency", "effectiveness", "success", "failure",
    
    # Performance Issues
    "weak", "weakness", "weaknesses", "struggling", "struggle", "difficulty", "problem", "issue",
    "challenge", "obstacle", "barrier", "limitation", "constraint", "bottleneck", "gap",
    "deficiency", "shortcoming", "fault", "flaw", "mistake", "error", "failure", "setback",
    
    # Skill Improvement
    "skill development", "skill building", "upskilling", "reskilling", "learning", "training",
    "practice", "rehearsal", "drill", "exercise", "coaching", "mentoring", "guidance",
    "instruction", "teaching", "tutoring", "feedback", "critique", "review",
    
    # Time Management Performance
    "time management", "productivity", "efficiency", "organization", "planning", "scheduling",
    "prioritizing", "multitasking", "focus", "concentration", "attention", "mindfulness",
    "procrastination", "delay", "deadline", "punctuality", "speed", "pace",
    
    # Mental Performance
    "mental performance", "cognitive", "brain", "memory", "recall", "retention", "concentration",
    "focus", "attention", "alertness", "awareness", "clarity", "intelligence", "reasoning",
    "logic", "analysis", "critical thinking", "problem solving", "creativity",
    
    # Work Performance
    "work performance", "job performance", "productivity", "quality", "accuracy", "precision",
    "reliability", "consistency", "innovation", "initiative", "leadership", "teamwork",
    "collaboration", "communication", "presentation", "negotiation",
    
    # Performance Strategies
    "strategy", "method", "technique", "approach", "system", "process", "procedure", "routine",
    "habit", "practice", "discipline", "structure", "framework", "model", "plan",
    "formula", "tip", "trick", "hack", "best practice",
    
    # Performance Tracking
    "track", "tracking", "monitor", "monitoring", "record", "log", "journal", "diary",
    "progress report", "assessment", "evaluation", "analysis", "review", "audit",
    "test", "measurement", "data", "statistics", "graph", "chart", "dashboard",
    
    # Performance Mindset
    "mindset", "attitude", "mentality", "confidence", "self-confidence", "self-esteem",
    "belief", "trust", "courage", "ambitious", "driven", "motivated", "inspired",
    "passionate", "enthusiastic", "positive", "determination", "commitment", "dedication",
    
    # Performance Obstacles
    "stress", "anxiety", "pressure", "tension", "nervousness", "fear", "doubt", "uncertainty",
    "confusion", "overwhelm", "burnout", "fatigue", "exhaustion", "laziness", "negative",
    "pessimistic", "discouragement", "frustration", "impatience",
    
    # Competition
    "compete", "competition", "competitive", "rival", "opponent", "peer", "comparison", "compare",
    "rank", "ranking", "position", "standing", "level", "standard", "benchmark", "best",
    "top", "winner", "champion", "leader", "first"
]

# WELFARE KEYWORDS (300 total)
welfare_keywords = [
    # Core Welfare Terms
    "welfare", "wellbeing", "well-being", "wellness", "health", "mental health", "emotional health",
    "psychological", "balance", "harmony", "peace", "serenity", "contentment", "satisfaction",
    "fulfillment", "happiness", "joy", "comfort",
    
    # Mental Health Conditions
    "stress", "anxiety", "depression", "panic", "worry", "fear", "phobia", "trauma", "ptsd",
    "burnout", "overwhelm", "exhaustion", "fatigue", "insomnia", "sleep", "mood", "bipolar",
    "ocd", "adhd", "eating disorder", "addiction", "substance abuse", "self-harm",
    
    # Emotional States
    "emotion", "emotions", "emotional", "feeling", "feelings", "sad", "sadness", "angry", "anger",
    "frustrated", "frustration", "disappointed", "disappointment", "lonely", "loneliness",
    "scared", "afraid", "nervous", "worried", "confused", "overwhelmed", "excited", "happy",
    
    # Stress and Pressure
    "pressure", "tension", "strain", "burden", "load", "weight", "heavy", "difficult", "hard",
    "challenging", "demanding", "exhausting", "draining", "overwhelming", "too much", "can't cope",
    "breaking point", "edge", "limit", "threshold", "tolerance", "endurance", "resilience",
    
    # Coping and Support
    "cope", "coping", "manage", "handle", "deal with", "face", "confront", "overcome", "survive",
    "support", "help", "assistance", "aid", "guidance", "advice", "counseling", "therapy",
    "therapist", "counselor", "psychologist", "psychiatrist", "social worker", "mentor",
    
    # Self-Care
    "self-care", "self-love", "self-compassion", "self-acceptance", "mindfulness", "meditation",
    "relaxation", "breathing", "yoga", "exercise", "fitness", "nutrition", "diet", "sleep",
    "rest", "recreation", "hobby", "hobbies", "fun", "enjoyment", "leisure", "downtime",
    
    # Relationships
    "relationship", "relationships", "family", "friends", "social", "community", "connection",
    "isolation", "alone", "lonely", "support system", "network", "bond", "attachment",
    "communication", "conflict", "argument", "fight", "disagreement", "misunderstanding",
    
    # Life Challenges
    "problem", "problems", "issue", "issues", "crisis", "emergency", "disaster", "tragedy",
    "loss", "grief", "death", "divorce", "separation", "breakup", "unemployment", "financial",
    "money", "debt", "poverty", "abuse", "violence", "discrimination", "bullying",
    
    # Academic Stress
    "academic stress", "study stress", "exam anxiety", "test anxiety", "performance anxiety",
    "perfectionism", "fear of failure", "imposter syndrome", "comparison", "competition",
    "pressure to succeed", "high expectations", "workload", "deadline stress",
    
    # Work-Life Balance
    "work-life balance", "balance", "juggle", "priorities", "boundaries", "overwork",
    "workaholic", "career stress", "job stress", "workplace", "boss", "colleagues",
    "deadlines", "meetings", "schedule", "flexibility", "remote work",
    
    # Physical Symptoms
    "headache", "migraine", "stomach", "nausea", "appetite", "weight", "muscle tension",
    "back pain", "chest pain", "heart", "breathing", "dizzy", "tired", "energy", "sick",
    "illness", "immune system", "recovery", "healing", "medicine", "doctor", "medical",
    
    # Crisis and Emergency
    "crisis", "emergency", "urgent", "immediate", "help needed", "desperate", "hopeless",
    "suicidal", "self-harm", "danger", "risk", "threat", "violence", "abuse", "trauma",
    "hotline", "emergency services", "crisis intervention", "intervention",
    
    # Recovery and Healing  
    "recovery", "healing", "treatment", "therapy", "medication", "improvement", "better", "progress",
    "breakthrough", "milestone", "success", "achievement", "growth", "development", "change",
    "transformation", "renewal", "fresh start", "new beginning", "hope", "optimism",
    
    # Positive Psychology
    "gratitude", "thankful", "appreciation", "blessing", "positive", "optimism", "hope",
    "faith", "belief", "trust", "love", "compassion", "kindness", "empathy", "understanding",
    "patience", "tolerance", "acceptance", "forgiveness", "peace", "calm", "tranquil",
    
    # Warning Signs
    "warning signs", "red flags", "symptoms", "indicators", "signs", "changes", "different",
    "unusual", "concerning", "worrying", "alarming", "dangerous", "risky", "harmful",
    "destructive", "negative", "decline", "deterioration", "setback", "relapse"
]

# Create the comprehensive keyword mapping
keyword_map = {}

# Add all keywords to the mapping
for keyword in academic_keywords:
    keyword_map[keyword.lower()] = academic

for keyword in career_keywords:
    keyword_map[keyword.lower()] = career

for keyword in performance_keywords:
    keyword_map[keyword.lower()] = performance

for keyword in welfare_keywords:
    keyword_map[keyword.lower()] = welfare

# Export for use in main application
__all__ = ['academic_keywords', 'career_keywords', 'performance_keywords', 'welfare_keywords', 'keyword_map']