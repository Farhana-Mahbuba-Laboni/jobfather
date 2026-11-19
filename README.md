# JobFather (JobFinder) — AI UX Job Bot

> Autonomous daily AI agent that scrapes, filters, and delivers targeted UX & Product Design opportunities directly to Telegram, tailored for a B.Sc in CSE graduate targeting 0–1 year experience roles in Bangladesh and Worldwide Remote.

---

## 1. Candidate Profile & Strategic Advantages

- **Academic Background**: B.Sc in Computer Science & Engineering (CSE).
- **Target Experience Level**: Entry-level, Junior, Internships, Trainee, or 0–1 year experience (no experience required; 0–2 years considered if negotiable).
- **Competitive Advantage**: The CSE degree unlocks technical UX niches (Design Engineer, UX Engineer, Design System Specialist) and satisfies the mandatory "B.Sc in CSE/CS" hiring requirement at major software exporters (Therap, Brain Station 23, BJIT, Cefalo, Selise, etc.).

### 13 Target UX Disciplines
1. **UX Designer**
2. **UX/UI Designer / UI/UX Designer**
3. **Product Designer**
4. **UX Researcher**
5. **Interaction Designer**
6. **Information Architect**
7. **UX Strategist**
8. **Service Designer**
9. **Accessibility Specialist**
10. **AI UX Designer**
11. **AI Agent Designer** (Autonomous Experience Designer)
12. **Design Engineer** (UX Engineer)
13. **Design System Specialist**

---

## 2. Directory Structure & Files

```
jobfinder/
├── jobfather.py         # Main execution script with 8 scraping pipelines & Gemini AI
├── requirements.txt     # Python dependencies (requests, beautifulsoup4, google-genai)
├── seen_jobs.json       # Deduplication history (prevents duplicate Telegram alerts)
└── README.md            # Comprehensive system documentation and operational runbook
```

- **Automation Workflow**: [`.github/workflows/daily_jobfather.yml`](file:///Users/farhanamahbuba/Downloads/claude-for-designers-main/.github/workflows/daily_jobfather.yml) (Runs daily at 8:30 AM BST / 2:30 AM UTC)
- **GitHub Repository**: [https://github.com/labonifarhana857-commits/jobfather.git](https://github.com/labonifarhana857-commits/jobfather.git)

---

## 3. Integrations & Configuration (GitHub Secrets)

The bot loads all sensitive keys securely from environment variables. When running in GitHub Actions, configure these in **Repository Settings > Secrets and variables > Actions**:

| Secret Name | Description | Example / Format |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Bot authorization token from `@BotFather` | `1234567890:ABCdefGHIjklMNOpqrs` |
| `TELEGRAM_CHAT_ID` | Your personal or group chat ID | `8468561197` |
| `GEMINI_API_KEY` | Google AI Studio Gemini API Key | `AIzaSy...` |
| `APIFY_TOKEN` | Apify Console API Token (for Facebook scrapers) | `apify_api_...` |

---

## 4. The 8 Live Scraping Pipelines

1. **LinkedIn Direct Guest API**: Scrapes live BD and Worldwide Remote entry-level UX circulars across Bangladesh and global remote queries.
2. **Remotive Official API**: Direct JSON endpoint querying active global remote design roles.
3. **We Work Remotely (WWR)**: XML RSS feed parsing worldwide remote product and UX design postings.
4. **RemoteOK Direct API**: Direct JSON feed for tech startup remote design roles.
5. **Bdjobs Official API & Specialist Design Boards**: Direct JSON API connection to Bdjobs (`api.bdjobs.com`), UI/UX Jobs Board Bangladesh (`uiuxjobsboard.com`), JobTogether Remote (`jobtogether.com`), Careerjet (BD & Global), and RemoteRocketship.
6. **All 5 Target Bangladesh Facebook Groups (via Apify & Feeds)**:
   - [UX Bangladesh](https://www.facebook.com/groups/uxbangladesh/)
   - [BD UI/UX Designers](https://www.facebook.com/groups/bduiuxdesigners/)
   - [UI/UX Bangladesh Community (237536162264896)](https://www.facebook.com/groups/237536162264896/)
   - [UI/UX BD](https://www.facebook.com/groups/uiuxbd/)
   - [UIUX Bangladesh](https://www.facebook.com/groups/UIUXBangladesh/)
7. **Tech Startups (Himalayas & Wellfound)**: Official Himalayas JSON API (`himalayas.app`) and Wellfound seed/series-A tech startup design roles.
8. **Top Bangladesh Tech Directory**:
   - **Telecoms**: Grameenphone, Banglalink, Robi Axiata
   - **MNCs & Enterprise**: Daraz (Alibaba), Optimizely, Walton Digi-Tech, TigerIT, a2i
   - **Fintech & Startups**: bKash, Pathao, Chaldal, 10 Minute School, Shikho, Jatri, ShopUp
   - **Software Exporters**: Therap BD, Brain Station 23, Cefalo, Selise, BJIT, Kaz Software, Kona SL
   - **SaaS & Agencies**: Ollyo, WPDeveloper, weDevs, Themeum, Musemind, Augmedix

---

## 5. AI Filtering & Classification Rules

1. **Graphic Design Trap Filter**: Discards roles primarily asking for social media banners, marketing flyers, or video editing.
2. **Experience Guardrail**: Strictly prioritizes 0–1 year / internships / freshers. If strict 0-year roles are scarce, negotiable 0–2 year roles are included as recommended matches.
3. **CSE Advantage Badge**: Automatically tags roles mentioning CSE/IT degrees or technical design (e.g. Design Systems, frontend bridging) with `🌟 CSE Advantage: ⭐ High Match!`.
4. **Output Card Schema**:
   ```
   📌 [Job Title] - [Company Name]
   • 🏢 Industry: [Actual business domain: FinTech / HealthTech / E-Commerce / EdTech / Enterprise SaaS / Telecom / Offshore IT / Agency]
   • 🌐 Source: [e.g. LinkedIn / Bdjobs / UI/UX Jobs Board / Facebook Community / Remotive / WWR / RemoteOK / JobTogether / Wellfound]
   • Type: [Internship / Part-time / Full-time / Remote / Hybrid]
   • 📍 Location: [e.g. Dhaka (Bashundhara/Gulshan/Banani/Dhanmondi/Uttara) or Remote Worldwide]
   • 💵 Compensation: [Paid / Unpaid / Competitive / Not specified]
   • 🌟 CSE Advantage: [⭐ High Match - Mentions CSE or Technical UX! / Good UX match]
   • Summary: [1-2 sentences on what they are building and key design requirements]
   • Deadline: [Application date or 'Not mentioned']
   • Link: [Direct URL]
   ```
5. **JobFather's Take**: A brief 1-line personalized recommendation or application strategy tip at the end of each digest.

---

## 6. How to Run

### Local Execution:
```bash
cd /Users/farhanamahbuba/Downloads/claude-for-designers-main/jobfinder
pip install -r requirements.txt
python jobfather.py
```

### GitHub Actions Schedule:
- The GitHub Actions workflow runs autonomously every day at `8:30 AM BST` (`02:30 UTC`).
- You can trigger a run at any time via the **Workflow Dispatch** button in your GitHub repository actions tab.
