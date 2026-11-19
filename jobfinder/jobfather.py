import os
import json
import time
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# --- CONFIGURATION (Loaded securely from Environment Variables / GitHub Secrets) ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

DB_FILE = os.path.join(os.path.dirname(__file__), "seen_jobs.json")

STEALTH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,bn;q=0.8"
}

def load_seen_jobs():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen_jobs(seen_set):
    trimmed = list(seen_set)[-500:]
    try:
        with open(DB_FILE, "w") as f:
            json.dump(trimmed, f, indent=2)
    except Exception as e:
        print(f"Notice saving seen database: {e}")

def send_telegram_message(message_text):
    """Sends formatted message(s) to Telegram, splitting automatically if over Telegram's 4096-char limit."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    chunks = []
    if len(message_text) <= 3900:
        chunks = [message_text]
    else:
        current_chunk = ""
        for line in message_text.split("\n"):
            if len(current_chunk) + len(line) + 1 > 3900:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
        if current_chunk:
            chunks.append(current_chunk)

    for chunk in chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        try:
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code != 200:
                payload.pop("parse_mode", None)
                requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Error sending message to Telegram: {e}")

# --- 1. LINKEDIN DIRECT SCRAPER ---
def fetch_linkedin_jobs(session, seen_urls):
    print("🔍 [1/8] Checking LinkedIn Direct API (Bangladesh & Worldwide Remote)...")
    search_queries = [
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=UX%20Designer&location=Bangladesh",
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=UI%20UX%20Designer&location=Bangladesh",
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Product%20Designer&location=Bangladesh",
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=UX%20Researcher&location=Bangladesh",
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=UX&f_WT=2&f_E=1,2", # Remote Junior/Intern
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Product%20Designer&f_WT=2&f_E=1,2" # Remote Junior/Intern
    ]
    new_jobs = []
    for query_url in search_queries:
        try:
            res = session.get(query_url, headers=STEALTH_HEADERS, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for item in soup.find_all("li"):
                    title = item.find("h3", class_="base-search-card__title")
                    company = item.find("h4", class_="base-search-card__subtitle")
                    link = item.find("a", class_="base-card__full-link")
                    if title and link:
                        clean_url = link.get("href").split("?")[0]
                        if clean_url not in seen_urls:
                            new_jobs.append({
                                "source": "LinkedIn",
                                "title": title.text.strip(),
                                "company": company.text.strip() if company else "Company not listed",
                                "link": clean_url
                            })
        except Exception as e:
            print(f"LinkedIn notice: {e}")
    print(f"   -> Found {len(new_jobs)} openings on LinkedIn.")
    return new_jobs

# --- 2. REMOTIVE OFFICIAL API ---
def fetch_remotive_jobs(session, seen_urls):
    print("🔍 [2/8] Checking Remotive Official Design API...")
    jobs = []
    url = "https://remotive.com/api/remote-jobs?category=design"
    try:
        res = session.get(url, headers=STEALTH_HEADERS, timeout=12)
        if res.status_code == 200:
            data = res.json()
            job_list = data.get("jobs", [])
            for item in job_list[:15]:
                title = item.get("title", "")
                company = item.get("company_name", "Remote Company")
                apply_url = item.get("url", "")
                location = item.get("candidate_required_location", "Worldwide")
                if apply_url and apply_url not in seen_urls:
                    jobs.append({
                        "source": "Remotive",
                        "title": title,
                        "company": f"{company} ({location})",
                        "link": apply_url
                    })
    except Exception as e:
        print(f"Remotive notice: {e}")
    print(f"   -> Found {len(jobs)} openings on Remotive.")
    return jobs

# --- 3. WE WORK REMOTELY (WWR) OFFICIAL RSS FEED ---
def fetch_wwr_rss(session, seen_urls):
    print("🔍 [3/8] Checking We Work Remotely (WWR) Official Design Feed...")
    jobs = []
    url = "https://weworkremotely.com/categories/remote-design-jobs.rss"
    try:
        res = session.get(url, headers=STEALTH_HEADERS, timeout=10)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            for item in root.findall(".//item")[:12]:
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                desc = item.find("description").text if item.find("description") is not None else ""
                if link and link not in seen_urls:
                    jobs.append({
                        "source": "We Work Remotely (WWR)",
                        "title": title,
                        "company": "Remote Global Tech",
                        "summary": desc[:150] if desc else "",
                        "link": link
                    })
    except Exception as e:
        print(f"WWR feed notice: {e}")
    print(f"   -> Found {len(jobs)} openings on We Work Remotely.")
    return jobs

# --- 4. REMOTEOK DIRECT API ---
def fetch_remoteok_jobs(session, seen_urls):
    print("🔍 [4/8] Checking RemoteOK Official Design API...")
    jobs = []
    url = "https://remoteok.com/api?tag=design"
    try:
        res = session.get(url, headers=STEALTH_HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for item in data[1:15]:
                pos = item.get("position", "")
                company = item.get("company", "Remote Startup")
                apply_url = item.get("url", "")
                if apply_url and apply_url not in seen_urls:
                    jobs.append({
                        "source": "RemoteOK",
                        "title": pos,
                        "company": company,
                        "link": apply_url
                    })
    except Exception as e:
        print(f"RemoteOK notice: {e}")
    print(f"   -> Found {len(jobs)} openings on RemoteOK.")
    return jobs

# --- 5. BDJOBS OFFICIAL API, UI/UX JOBS BOARD, CAREERJET, JOBTOGETHER & PORTALS ---
def fetch_bd_and_remote_portals(session, seen_urls):
    print("🔍 [5/8] Checking Portals (Bdjobs Official API, UI/UX Jobs Board BD, Careerjet, JobTogether, RemoteRocketship)...")
    jobs = []

    # 1. Bdjobs Official JSON API (Fast, Direct, 100% Reliable)
    bdjobs_headers = {
        "User-Agent": STEALTH_HEADERS["User-Agent"],
        "Origin": "https://bdjobs.com",
        "Referer": "https://bdjobs.com/h/jobs/"
    }
    for term in ["UX", "UI%2FUX", "Product+Designer"]:
        try:
            api_url = f"https://api.bdjobs.com/jobs/api/v1/JobSearch/GetJobSearch?txtsearch={term}"
            res = session.get(api_url, headers=bdjobs_headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for item in data.get("data", [])[:15]:
                    job_id = item.get("Jobid")
                    title = item.get("jobTitle", "").strip()
                    comp = item.get("companyName", "Bdjobs Employer").strip()
                    deadline = item.get("deadline", "Not specified")
                    if job_id:
                        clean_link = f"https://bdjobs.com/h/details/{job_id}"
                        if clean_link not in seen_urls:
                            jobs.append({
                                "source": "Bdjobs",
                                "title": title,
                                "company": comp,
                                "deadline": deadline,
                                "link": clean_link
                            })
        except Exception as e:
            print(f"Bdjobs API ({term}) notice: {e}")

    # 2. UI/UX Jobs Board Bangladesh Direct Scrape
    try:
        uiux_url = "https://uiuxjobsboard.com/design-jobs/bangladesh"
        res = session.get(uiux_url, headers=STEALTH_HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.select("a[href*='/job/']"):
                title = a_tag.text.strip().replace("\n", " ")
                href = a_tag.get("href", "")
                if href and title and len(title) > 3:
                    clean_link = f"https://uiuxjobsboard.com{href}" if not href.startswith("http") else href
                    if clean_link not in seen_urls:
                        jobs.append({
                            "source": "UI/UX Jobs Board",
                            "title": title,
                            "company": "UI/UX Jobs Board Employer",
                            "link": clean_link
                        })
    except Exception as e:
        print(f"UI/UX Jobs Board direct notice: {e}")

    # 3. Aggregators: Careerjet (BD & Global), JobTogether, RemoteRocketship, UI/UX Jobs Board, NextJobz, DhakaCareers
    queries = [
        '(site:jobs.bdjobs.com OR site:careerjet.com.bd OR site:careerjet.com) ("UX" OR "Product Designer" OR "UI/UX")',
        'site:uiuxjobsboard.com ("Bangladesh" OR "Remote") ("UX" OR "Product Designer")',
        'site:jobtogether.com ("UX" OR "Product Designer" OR "UI/UX") ("Junior" OR "Intern" OR "Entry" OR "Remote")',
        'site:remoterocketship.com ("UX" OR "Product Designer") ("junior" OR "intern")',
        '(site:nextjobz.com.bd OR site:dhakacareers.com) ("UX" OR "Product Designer" OR "UI/UX")'
    ]
    headers = {**STEALTH_HEADERS, "Referer": "https://html.duckduckgo.com/"}
    for q in queries:
        try:
            time.sleep(1)
            res = session.post("https://html.duckduckgo.com/html/", data={"q": q}, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for item in soup.find_all("div", class_="result__body")[:5]:
                    snippet = item.find("a", class_="result__snippet")
                    link_tag = item.find("a", class_="result__url")
                    if snippet and link_tag:
                        clean_link = link_tag.get("href", "").strip()
                        if clean_link and clean_link not in seen_urls:
                            src_name = "Job Portal"
                            comp_name = "Hiring Company"
                            if "bdjobs.com" in clean_link:
                                src_name = "Bdjobs"
                            elif "uiuxjobsboard.com" in clean_link:
                                src_name = "UI/UX Jobs Board"
                            elif "jobtogether.com" in clean_link:
                                src_name = "JobTogether"
                            elif "careerjet" in clean_link:
                                src_name = "Careerjet"
                            elif "remoterocketship" in clean_link:
                                src_name = "RemoteRocketship"

                            jobs.append({
                                "source": src_name,
                                "title": snippet.text.strip()[:140],
                                "company": comp_name,
                                "link": clean_link
                            })
        except Exception as e:
            print(f"Portal notice: {e}")

    print(f"   -> Found {len(jobs)} openings across all job portals & specialist boards.")
    return jobs

# --- 6. ALL 5 BANGLADESH FACEBOOK UX GROUPS (APIFY & COMMUNITY FEEDS) ---
def fetch_facebook_via_apify(session, seen_urls):
    print("🔍 [6/8] Checking All 5 Bangladesh Facebook Groups (24-Hour Coverage)...")
    posts = []
    
    # 1. Apify Cloud Scraper with extended 24-hour depth
    try:
        url = f"https://api.apify.com/v2/acts/apify~facebook-groups-scraper/run-sync-get-dataset-items?token={APIFY_TOKEN}&timeout=70"
        payload = {
            "startUrls": [
                {"url": "https://www.facebook.com/groups/uxbangladesh/"},
                {"url": "https://www.facebook.com/groups/bduiuxdesigners/"},
                {"url": "https://www.facebook.com/groups/237536162264896/"},
                {"url": "https://www.facebook.com/groups/uiuxbd/"},
                {"url": "https://www.facebook.com/groups/UIUXBangladesh/"}
            ],
            "maxPosts": 15,
            "maxComments": 0
        }
        headers = {"Content-Type": "application/json"}
        res = requests.post(url, json=payload, headers=headers, timeout=75)
        if res.status_code in [200, 201]:
            items = res.json()
            if isinstance(items, list):
                for item in items:
                    txt = item.get("text") or item.get("postText") or item.get("message") or ""
                    post_link = item.get("url") or item.get("postUrl") or "https://facebook.com/groups/uxbangladesh/"
                    if txt and post_link not in seen_urls:
                        posts.append({
                            "source": "Facebook Group Post (Apify)",
                            "title": txt.replace("\n", " | ")[:150],
                            "company": item.get("groupTitle", "Bangladesh UX Community"),
                            "link": post_link
                        })
    except Exception as e:
        print(f"Apify Facebook notice: {e}")

    # 2. Community Search Fallback for 24-Hour Facebook Group Hiring Posts
    if len(posts) < 2:
        try:
            fb_queries = [
                'site:facebook.com/groups ("uxbangladesh" OR "bduiuxdesigners" OR "uiuxbd") ("hiring" OR "looking for" OR "intern")',
                'site:facebook.com/groups ("UI/UX" OR "Product Designer" OR "Design Engineer") ("Dhaka" OR "Bangladesh") ("hiring" OR "intern")'
            ]
            headers = {**STEALTH_HEADERS, "Referer": "https://html.duckduckgo.com/"}
            for q in fb_queries:
                time.sleep(1)
                res = session.post("https://html.duckduckgo.com/html/", data={"q": q}, headers=headers, timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    for item in soup.find_all("div", class_="result__body")[:5]:
                        snippet = item.find("a", class_="result__snippet")
                        link_tag = item.find("a", class_="result__url")
                        if snippet and link_tag:
                            clean_link = link_tag.get("href", "").strip()
                            if clean_link and clean_link not in seen_urls:
                                posts.append({
                                    "source": "Facebook Community Lead",
                                    "title": snippet.text.strip()[:140],
                                    "company": "Facebook Design Community",
                                    "link": clean_link
                                })
        except Exception as e:
            print(f"Facebook community fallback notice: {e}")

    print(f"   -> Found {len(posts)} live posts across Facebook design groups.")
    return posts

# --- 7. TECH STARTUPS (HIMALAYAS & WELLFOUND) ---
def fetch_wellfound_jobs(session, seen_urls):
    print("🔍 [7/8] Checking Tech Startup & Seed-Stage Portals (Himalayas & Wellfound)...")
    jobs = []

    # 1. Himalayas Official Remote Tech Startup API
    try:
        res = session.get("https://himalayas.app/jobs/api?category=design", headers=STEALTH_HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for item in data.get("jobs", [])[:20]:
                title = item.get("title", "")
                company = item.get("companyName", "Tech Startup")
                link = item.get("applicationLink") or item.get("url") or ""
                if link and link not in seen_urls:
                    jobs.append({
                        "source": "Himalayas Startup",
                        "title": title,
                        "company": company,
                        "link": link
                    })
    except Exception as e:
        print(f"Himalayas API notice: {e}")

    # 2. Wellfound / AngelList
    try:
        url = "https://html.duckduckgo.com/html/"
        q = 'site:wellfound.com/jobs ("UX Designer" OR "Product Designer") ("junior" OR "entry" OR "intern")'
        headers = {**STEALTH_HEADERS, "Referer": "https://html.duckduckgo.com/"}
        res = session.post(url, data={"q": q}, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for item in soup.find_all("div", class_="result__body")[:6]:
                snippet = item.find("a", class_="result__snippet")
                link_tag = item.find("a", class_="result__url")
                if snippet and link_tag:
                    clean_link = link_tag.get("href", "").strip()
                    if clean_link and clean_link not in seen_urls:
                        jobs.append({
                            "source": "Wellfound (AngelList)",
                            "title": snippet.text.strip()[:140],
                            "company": "Seed/Series-A Startup",
                            "link": clean_link
                        })
    except Exception as e:
        print(f"Wellfound notice: {e}")
    print(f"   -> Found {len(jobs)} startup openings across Himalayas & Wellfound.")
    return jobs

# --- 8. COMPLETE DIRECTORY OF BD TECH GIANTS, STARTUPS, SAAS & TELECOMS ---
def fetch_complete_bd_companies(session, seen_urls):
    """
    Directly monitors ALL major BD employers:
    - Telecoms: Grameenphone, Banglalink, Robi
    - MNCs & Conglomerates: Daraz, Optimizely, Walton, TigerIT, Foodpanda
    - Fintech & Top Startups: bKash, Pathao, Chaldal, 10 Minute School, Shikho, Jatri, ShopUp, Arogga
    - Software Exporters: Therap BD, Brain Station 23, Cefalo, Selise, BJIT, Kaz Software, Kona SL, Enosis
    - SaaS, Design Systems & Agencies: WPDeveloper, weDevs, Ollyo, Themeum, Musemind, Augmedix
    """
    print("🔍 [8/8] Checking All BD Tech Giants (Therap, Brain Station 23, bKash, Pathao, Cefalo, Selise, BJIT, Daraz, Ollyo, WPDeveloper, weDevs)...")
    jobs = []

    # 1. Direct Company Search for BD Tech Employers
    target_bd_companies = [
        "Therap", "Brain Station 23", "bKash", "Pathao", "Cefalo", "Selise",
        "BJIT", "Daraz", "10 Minute School", "Ollyo", "WPDeveloper", "weDevs"
    ]
    for comp in target_bd_companies:
        try:
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={comp.replace(' ', '%20')}%20Design&location=Bangladesh"
            res = session.get(url, headers=STEALTH_HEADERS, timeout=8)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for item in soup.find_all("li"):
                    title = item.find("h3", class_="base-search-card__title")
                    c_name = item.find("h4", class_="base-search-card__subtitle")
                    link = item.find("a", class_="base-card__full-link")
                    if title and link:
                        clean_url = link.get("href").split("?")[0]
                        if clean_url not in seen_urls:
                            jobs.append({
                                "source": f"BD Tech Giant ({comp})",
                                "title": title.text.strip(),
                                "company": c_name.text.strip() if c_name else comp,
                                "link": clean_url
                            })
        except Exception as e:
            print(f"Notice checking {comp}: {e}")

    # 2. Portal & Web Queries for BD Tech Directory
    queries = [
        # Telecoms & MNCs
        '(site:grameenphone.com OR site:banglalink.net OR site:robi.com.bd OR site:careers.daraz.com OR site:optimizely.com) ("UX" OR "Product Designer" OR "UI/UX")',
        # Hardware, Enterprise & Identity
        '(site:waltonbd.com OR site:tigerit.com OR site:a2i.gov.bd) ("UX" OR "Designer" OR "UI/UX")',
        # Funded Startups & Fintech
        '(site:bkash.com OR site:pathao.com OR site:chaldal.com OR site:10minuteschool.com OR site:shikho.com OR site:jatri.co OR site:shopup.org) ("UX" OR "Product Designer")',
        # Top Software Exporters (Therap, Brain Station, Cefalo, Selise, BJIT, Kaz, Kona SL, Enosis)
        '(site:therapbd.com OR site:brainstation-23.com OR site:cefalo.com OR site:selisegroup.com OR site:bjitgroup.com OR site:kaz.com.bd OR site:konasl.com) ("UX" OR "Design" OR "Product Designer")',
        # SaaS, Design Systems & HealthTech (Ollyo, WPDeveloper, weDevs, Themeum, Musemind, Augmedix)
        '(site:ollyo.com OR site:wpdeveloper.com OR site:wedevs.com OR site:themeum.com OR site:musemind.agency OR site:augmedix.com) ("UX" OR "UI/UX" OR "Designer" OR "Design System")'
    ]
    headers = {**STEALTH_HEADERS, "Referer": "https://html.duckduckgo.com/"}
    for q in queries:
        try:
            time.sleep(1)
            res = session.post("https://html.duckduckgo.com/html/", data={"q": q}, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for item in soup.find_all("div", class_="result__body")[:5]:
                    snippet = item.find("a", class_="result__snippet")
                    link_tag = item.find("a", class_="result__url")
                    if snippet and link_tag:
                        clean_link = link_tag.get("href", "").strip()
                        if clean_link and clean_link not in seen_urls:
                            jobs.append({
                                "source": "BD Tech / Enterprise / Startup",
                                "title": snippet.text.strip()[:140],
                                "company": "Bangladesh Tech Employer",
                                "link": clean_link
                            })
        except Exception as e:
            print(f"Company search notice: {e}")
    print(f"   -> Found {len(jobs)} openings across all BD tech giants & startups.")
    return jobs

# --- AI ANALYSIS & TELEGRAM DIGEST ---
def filter_with_ai_and_notify():
    seen_urls = load_seen_jobs()
    print(f"📚 Memory database loaded: {len(seen_urls)} previous jobs tracked.")

    with requests.Session() as session:
        session.headers.update(STEALTH_HEADERS)
        
        linkedin_jobs = fetch_linkedin_jobs(session, seen_urls)
        remotive_jobs = fetch_remotive_jobs(session, seen_urls)
        wwr_jobs = fetch_wwr_rss(session, seen_urls)
        remoteok_jobs = fetch_remoteok_jobs(session, seen_urls)
        portal_jobs = fetch_bd_and_remote_portals(session, seen_urls)
        fb_jobs = fetch_facebook_via_apify(session, seen_urls)
        wellfound_jobs = fetch_wellfound_jobs(session, seen_urls)
        bd_companies_jobs = fetch_complete_bd_companies(session, seen_urls)

    combined_data = (
        linkedin_jobs + remotive_jobs + wwr_jobs + 
        remoteok_jobs + portal_jobs + fb_jobs + 
        wellfound_jobs + bd_companies_jobs
    )
    print(f"\n📊 TOTAL REAL JOBS FOUND ACROSS ALL 8 PIPELINES: {len(combined_data)}")

    if not combined_data:
        send_telegram_message("🔍 *JobFather Daily Check:*\nNo brand-new UX circulars posted since your last alert. Check back tomorrow!")
        return

    print("🤖 Processing with Gemini AI (Filtering 13 UX Roles, CSE Advantage & Categorizing)...")

    prompt = f"""
    You are 'JobFather', an expert career mentor for a candidate who holds a B.Sc in CSE and wants an entry-level/junior UX or Product Design position in Bangladesh or Worldwide Remote.

    Here is the full batch of real scraped jobs directly from LinkedIn, Remotive, We Work Remotely, RemoteOK, Bdjobs/Careerjet/Nextjobz, Wellfound Startups, BD Tech Giants (GP/Banglalink/Robi/bKash/Pathao/Chaldal/10MS/Therap/Brain Station/Ollyo/WPDeveloper), and live Facebook Groups:
    {combined_data}

    YOUR GOAL:
    1. Filter for these 13 target UX/Product Design disciplines:
       - UX Designer, UI/UX Designer, Product Designer, UX Researcher, Interaction Designer, Information Architect, UX Strategist, Service Designer, Accessibility Specialist, AI UX Designer, AI Agent Designer, Design Engineer (UX Engineer), Design System Specialist.
    2. Discard obvious Graphic Design / social media banner / flyer jobs.
    3. Look for roles welcoming beginners (Intern, Trainee, Junior, 0-1 year, or freshers). If strict 0-year roles are scarce, include the best junior/entry roles (0-2 years, negotiable, or intern) as 'Recommended Matches' so the candidate has active leads.
    4. ACCURATE BUSINESS INDUSTRY CLASSIFICATION:
       - Identify the hiring company's actual business domain (e.g. FinTech, Telecom & Super-Apps, Enterprise SaaS, HealthTech, EdTech, E-Commerce & Logistics, Software Exporter / Offshore IT, AI & Autonomous Tech, Digital Product Studio / Agency).
       - CRUCIAL: NEVER use the job portal or scraping medium (like Bdjobs, LinkedIn, Careerjet, RemoteRocketship, UI/UX Jobs Board, JobTogether, or Facebook) as the Industry! The job board is just the medium and belongs under '🌐 Source'.

    Format each job strictly as:
    📌 *[Job Title]* - [Company Name]
    • *🏢 Industry:* [Actual business domain: e.g. FinTech / HealthTech / E-Commerce / EdTech / Enterprise SaaS / Telecom / Offshore IT / Agency]
    • *🌐 Source:* [e.g. LinkedIn / Bdjobs / UI/UX Jobs Board / Facebook Community / Remotive / WWR / RemoteOK / JobTogether / Wellfound]
    • *Type:* [Internship / Part-time / Full-time / Remote / Hybrid]
    • *📍 Location:* [e.g. Dhaka (Bashundhara/Gulshan/Banani/Dhanmondi/Uttara) or Remote Worldwide]
    • *💵 Compensation:* [Paid / Unpaid / Competitive / Not specified]
    • *🌟 CSE Advantage:* [⭐ High Match - Mentions CSE or Technical UX! / Good UX match]
    • *Summary:* [1-2 sentences on what they are building and key design requirements]
    • *Deadline:* [Application date or 'Not mentioned']
    • *Link:* [Direct URL]

    Also include a brief 1-line 'JobFather's Take' at the end with encouragement or an application tip!
    """

    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)

    models_to_try = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"]
    response = None

    for model_name in models_to_try:
        print(f"🤖 Analyzing with Gemini ({model_name})...")
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    print(f"✅ AI analysis complete using {model_name}!")
                    break
            except Exception as e:
                print(f"Notice ({model_name}, attempt {attempt+1}): {e}")
                time.sleep(2)
        if response and response.text:
            break

    if not response or not response.text:
        ai_text = "⚠️ Gemini API temporary high demand. Seen memory preserved so no jobs are lost. Will retry on next run."
        send_telegram_message(f"🎯 *JobFather Notice:*\n\n{ai_text}")
        print("⚠️ AI generation unavailable. Preserving jobs in memory for next run.")
        return

    ai_text = response.text
    final_message = f"🎯 *JobFather Daily UX Digest (All Sources Complete Edition):*\n\n{ai_text}"
    send_telegram_message(final_message)
    print("✅ Notification sent to Telegram with categorized job leads!")

    for item in combined_data:
        if "link" in item and item["link"]:
            seen_urls.add(item["link"])
    save_seen_jobs(seen_urls)
    print(f"💾 Saved {len(seen_urls)} total job links in seen memory database.")

if __name__ == "__main__":
    filter_with_ai_and_notify()
