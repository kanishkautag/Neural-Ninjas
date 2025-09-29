# SkillMorph 💼

**A career recommendation platform** built during a hackathon.  
It combines live job listings, course suggestions, ATS-style resume feedback, and personalized roadmap generation — all powered by APIs, datasets, and AI logic.

---

## 📌 Table of Contents

- [Features](#-features)  
- [Architecture & Tech Stack](#-architecture--tech-stack)  
- [How It Works / Flow](#-how-it-works--flow)  
- [Demo / Screenshots](#-demo--screenshots)  
- [Your Role / Contributions](#-your-role--contributions)  
- [Setup / Installation](#-setup--installation)  
- [Usage](#-usage)  
- [Future Enhancements](#-future-enhancements)  
- [Credits & Acknowledgements](#-credits--acknowledgements)  
- [License](#-license)  

---

## ✨ Features

- **Live Job Listings**  
  Fetches current job openings using the Serper API and displays them dynamically.

- **Authentication / User Management**  
  Sign up, login, password reset, session management via **Firebase Auth**.

- **Course Recommendations**  
  Based on the user’s level (beginner / intermediate / advanced) and domain, suggests relevant Udemy courses (datasets & links).

- **ATS-Style Resume Evaluation & Recommendations**  
  Parses uploaded resumes, scores them (keyword match, structure), and gives suggestions to improve chances with Applicant Tracking Systems.

- **Roadmap Generator**  
  Generates a personalized career roadmap (skills, courses, milestones) depending on domain & current level.

- **Modular Backend / Frontend**  
  Clean separation of concerns, so each module (jobs, courses, ATS, roadmap) can be developed or improved independently.

---

## 🏗 Architecture & Tech Stack

| Component | Technology / Tools |
|----------|---------------------|
| Frontend | HTML, CSS, JavaScript (or React / Vue / your chosen framework) |
| Backend | Python / Node.js (or whichever you used) |
| API Integration | Serper API for job listings |
| Authentication | Firebase Auth |
| Course Dataset | Udemy dataset (pre-collected) |
| Resume Parsing / Scoring | Custom logic / NLP / regex / keyword matching |
| Hosting / Deployment (if any) | (Optional: add your hosting / server / cloud) |

---

## 🔄 How It Works / Flow

1. **Sign Up / Log In**  
   Users create an account or log in via Firebase; credentials are verified.

2. **Set Profile / Preferences**  
   User selects their domain (e.g. Data Science, Web Dev, etc.) and their current skill level.

3. **Job Listings Module**  
   The backend calls Serper API periodically (or on request) to fetch latest job listings; filters by domain; returns to frontend.

4. **Course Recommendation Module**  
   Based on the user’s preferences and level, the backend filters from Udemy dataset to suggest courses.

5. **Resume Upload & ATS Feedback**  
   Users upload their resume (PDF / DOC). The system parses text, checks for key sections, relevant keywords, structure, and outputs a score + suggestions.

6. **Roadmap Generation**  
   Combines all data (user profile, courses, jobs) to suggest milestones & steps (skills to learn, courses to take) over time.

## Demo/Screenshots
<img width="1695" height="836" alt="image" src="https://github.com/user-attachments/assets/07ee2569-d92a-4640-aa34-4ea65d67a41f" />


- Integrated **Serper API** for fetching and filtering live jobs.  
- Built **Course Recommendation logic** using the Udemy dataset (mapping levels, filtering domain courses).  
- Developed the **Roadmap Generator** module: algorithm that takes user input → outputs milestone path.  
- Assisted / improved the **ATS resume evaluation** logic, adding keyword matching & structural checks.  
- Frontend / UI enhancements: (if you worked on UI, state management, styling, etc.)  
- Wrote tests / documentation / debugging / integration.

---

## 🛠 Setup / Installation

> These instructions assume you have `git`, `Python` / `Node.js`, etc. installed.

```bash
# 1. Clone the repo (use your fork or branch)
git clone https://github.com/kanishkautag/Neural-Ninjas.git
cd Neural-Ninjas

# 2. Switch to the branch
git checkout kanishka

# 3. Backend setup
cd backend
# install dependencies, e.g.:
pip install -r requirements.txt
# or for Node:
npm install
# (any environment variables: Firebase config, Serper API key, etc.)

# 4. Frontend setup
cd ../frontend
npm install
# or yarn install

# 5. Run dev servers
# backend
cd ../backend && python app.py  # or npm start
# frontend
cd ../frontend && npm start

