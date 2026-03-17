from fastapi import FastAPI
from pydantic import BaseModel
import openai, sqlite3, re

app = FastAPI()

openai.api_key = "AIzaSyAtAc_Hqye2fQnDIVvyd6IkF_sJaNfHImo"

# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")

# ---------------- MODELS ----------------
class User(BaseModel):
    username: str
    password: str

class ResumeData(BaseModel):
    name: str
    role: str
    skills: str
    experience: str
    job_description: str

class ChatData(BaseModel):
    message: str

class PortfolioData(BaseModel):
    name: str
    projects: str

# ---------------- LOGIN ----------------
@app.post("/register")
def register(user: User):
    cursor.execute("INSERT INTO users VALUES (?,?)", (user.username, user.password))
    conn.commit()
    return {"msg": "User registered"}

@app.post("/login")
def login(user: User):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user.username, user.password))
    result = cursor.fetchone()
    return {"success": bool(result)}

# ---------------- RESUME + ATS ----------------
@app.post("/generate-resume")
def generate_resume(data: ResumeData):
    prompt = f"Create professional resume for {data.name}, {data.role}, {data.skills}, {data.experience}"

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    resume = response["choices"][0]["message"]["content"]

    jd_words = set(re.findall(r'\w+', data.job_description.lower()))
    resume_words = set(re.findall(r'\w+', resume.lower()))
    score = int((len(jd_words & resume_words)/len(jd_words))*100) if jd_words else 70

    return {"resume": resume, "ats_score": score}

# ---------------- PORTFOLIO ----------------
@app.post("/portfolio")
def portfolio(data: PortfolioData):
    prompt = f"Create portfolio content for {data.name} with projects {data.projects}"

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"portfolio": response["choices"][0]["message"]["content"]}

# ---------------- CHATBOT ----------------
@app.post("/chat")
def chat(data: ChatData):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": data.message}]
    )

    return {"reply": response["choices"][0]["message"]["content"]}