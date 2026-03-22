import os
import json
import markdown
from datetime import datetime
import pytz
from google import genai
from google.genai import types

# --- Configuration ---
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

client = genai.Client(api_key=API_KEY)

# Use gemini-2.5-pro for best reasoning and search capability
MODEL = "gemini-2.5-pro"

# File paths (relative to repo root)
TRACKER_FILE = "scripts/verse_tracker.json"
OUTPUT_FILE = "docs/index.html"

# --- Prompts ---
PROMPT_NEWS = """
You are a Senior News Editor and Intelligence Analyst specializing in Indian and Global affairs. Your task is to provide a comprehensive daily briefing with maximum signal and zero noise. Task: Synthesize the latest news based on the categories below. Data Source Constraints: Prioritize reporting from: India Today, Times of India, Deccan Herald, Hindustan Times, Mint, Cricbuzz, Cricinfo, BBC, Al Jazeera, Bangalore Mirror, TV9 Kannada, and Economic Times. Formatting Rules: Provide exactly 5 bullet points per section. Use a professional, objective tone. For prices/weather, provide current data points. Bold key entities (names, companies, locations). Sections to Populate: 1. Indian National News 2. Indian Sports News 3. Global Sports News 4. Indian Market News 5. Global Market News 6. Gold Price Analysis: Current rate for 22k/24k gold in Bangalore and Dublin (converted to INR). 7. AI Related News 8. Karnataka News 9. India-Centric Geopolitics 10. Trending on Twitter (X) India 11. Bangalore Deals/Sales 12. Dublin Deals/Sales 13. Upcoming Events (Dublin): Gigs, festivals, or conferences in the next 7 days. 14. Upcoming Events (Bangalore) 15. Weather Forecast: Today’s High/Low and conditions for Bangalore and Dublin.
"""

PROMPT_COMMUNICATION = """
Provide a daily exercise to improve Hiberno-English small talk, reduce filler words, and translate observational Kannada humor into Irish 'craic' for someone living in Dublin, County Dublin, Ireland. Include a specific phrase to practice and a social challenge.
"""

PROMPT_HOMES = """
Check for any new build residential developments that have recently received planning permission or announced upcoming releases in Dublin, Kildare, and Wicklow, specifically focusing on those under €500k suitable for a couple with a €120k+ income. Produce a brief, tabular summary of findings.
"""

PROMPT_FLIGHTS = """
Monitor round-trip flight prices from Dublin (DUB) to Bangalore (BLR) for 2 adults + 1 infant (lap). Cabin: Economy & Flexible Economy. Trip Type: Return. Stay Duration: 28 days EXACT (±1 day tolerance). DATE SEARCH WINDOW: Outbound between August 20 and October 9; Return 28 days after outbound. AIRLINE CONSTRAINT: Only Emirates, Qatar Airways, Etihad Airways, or Turkish Airlines (via ME hub). FILTERS: Max 1 stop preferred, total travel time < 22 hours, infant-friendly layover (1.5–4 hours). Avoid overnight layovers > 6 hours. DATA TO EXTRACT DAILY: Cheapest Economy and Flexible Economy fares, airline, layover city/duration, total travel time, price trend vs yesterday, best value date pair. OUTPUT FORMAT (STRICT TABLE): Date Checked | Airline | Outbound Date | Return Date | Economy Price | Flex Economy Price | Stops | Layover | Recommendation (Book/Wait). ALERT LOGIC: Alert if price drops ≥ 10% from 7-day average or total fare < €700 per adult. Provide daily summary with cheapest date combination, trend, and verdict (BOOK NOW or WAIT).
"""

# --- Helper Functions ---
def get_gita_prompt():
    try:
        with open(TRACKER_FILE, 'r') as f:
            data = json.load(f)
            chapter = data.get("chapter", 1)
            verse = data.get("verse", 1)
    except Exception as e:
        print(f"Error reading tracker: {e}")
        chapter, verse = 1, 1

    prompt = f"""
Provide the next verse of the Bhagavad Gita sequentially, starting with Chapter 1, Verse 1. For today's verse, provide Bhagavad Gita Chapter {chapter}, Verse {verse}: 
1. The actual verse in Kannada script. 
2. The meaning in English. 
3. A deeper meaning tailored for the 90s generation (millennials) with a practical example of how to apply it in modern daily life, in English. 
"""
    return prompt, chapter, verse

def update_tracker(chapter, verse):
    # Simplified Gita verse limits (approximate for the sake of daily advancement)
    verses_per_chapter = {
        1: 47, 2: 72, 3: 43, 4: 42, 5: 29, 6: 47, 7: 30, 8: 28, 9: 34, 
        10: 42, 11: 55, 12: 20, 13: 35, 14: 27, 15: 20, 16: 24, 17: 28, 18: 78
    }
    
    max_verses = verses_per_chapter.get(chapter, 20) # fallback
    
    next_verse = verse + 1
    next_chapter = chapter
    
    if next_verse > max_verses:
        next_verse = 1
        next_chapter += 1
    
    if next_chapter > 18:
        next_chapter = 1 # loop back if done
        
    try:
        with open(TRACKER_FILE, 'w') as f:
            json.dump({"chapter": next_chapter, "verse": next_verse}, f, indent=2)
    except Exception as e:
        print(f"Error saving tracker: {e}")

def call_gemini(prompt, use_search=False):
    print(f"Calling Gemini... (Search Grounding: {use_search})")
    
    config = types.GenerateContentConfig(
        temperature=0.3, # Keep it relatively deterministic
    )
    
    if use_search:
        # Enable Google Search tool for real-time data
        config.tools = [{"google_search": {}}]
        
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=config
        )
        return response.text
    except Exception as e:
        print(f"API Error: {e}")
        return f"**Error generating content:** {str(e)}"

# --- Main Logic ---
def generate_html_digest():
    dublin_tz = pytz.timezone('Europe/Dublin')
    now = datetime.now(dublin_tz)
    date_str = now.strftime("%A, %B %d, %Y")
    
    print(f"Starting Daily PA Generation for {date_str}")
    
    # 1. News (Needs real-time search)
    print("Generating News...")
    news_md = call_gemini(PROMPT_NEWS, use_search=True)
    
    # 2. Gita
    print("Generating Gita...")
    gita_prompt, gita_ch, gita_ve = get_gita_prompt()
    gita_md = call_gemini(gita_prompt, use_search=False)
    
    # 3. Communication
    print("Generating Communication...")
    comm_md = call_gemini(PROMPT_COMMUNICATION, use_search=False)
    
    # 4. Homes
    print("Generating Homes...")
    homes_md = call_gemini(PROMPT_HOMES, use_search=True)
    
    # 5. Flights
    print("Generating Flights...")
    flights_md = call_gemini(PROMPT_FLIGHTS, use_search=True)
    
    # Update state
    update_tracker(gita_ch, gita_ve)
    
    # Clean up markdown output
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily PA - {date_str}</title>
        <style>
            :root {{
                --bg: #0f172a; --surface: #1e293b; --text: #e2e8f0;
                --accent: #38bdf8; --border: #334155;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--bg); color: var(--text);
                line-height: 1.6; margin: 0; padding: 20px;
                max-width: 900px; margin: 0 auto;
            }}
            h1 {{ border-bottom: 2px solid var(--accent); padding-bottom: 10px; color: white; }}
            h2 {{ color: var(--accent); margin-top: 40px; border-bottom: 1px solid var(--border); padding-bottom: 5px; }}
            h3 {{ color: #94a3b8; }}
            .card {{
                background: var(--surface); border-radius: 12px;
                padding: 25px; margin-bottom: 30px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                border: 1px solid var(--border);
            }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid var(--border); padding: 12px; text-align: left; }}
            th {{ background-color: rgba(56, 189, 248, 0.1); color: var(--accent); }}
            a {{ color: var(--accent); text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .timestamp {{ font-size: 0.9em; color: #94a3b8; margin-bottom: 30px; }}
        </style>
    </head>
    <body>
        <h1>Daily Personal Assistant</h1>
        <div class="timestamp">Generated on {date_str} at {now.strftime("%H:%M")} Dublin Time</div>
        
        <div class="card">
            <h2>🌍 Daily Intelligence Briefing</h2>
            {markdown.markdown(news_md, extensions=['tables'])}
        </div>

        <div class="card">
            <h2>📿 Bhagavad Gita (Ch {gita_ch}, V {gita_ve})</h2>
            {markdown.markdown(gita_md)}
        </div>

        <div class="card">
            <h2>🗣️ Hiberno-English & Craic</h2>
            {markdown.markdown(comm_md)}
        </div>

        <div class="card">
            <h2>🏠 Ireland Property Radar</h2>
            {markdown.markdown(homes_md, extensions=['tables'])}
        </div>

        <div class="card">
            <h2>✈️ Dublin -> Bangalore Flight Monitor</h2>
            {markdown.markdown(flights_md, extensions=['tables'])}
        </div>
        
        <div style="text-align: center; margin-top: 50px; color: #64748b; font-size: 0.8em;">
            Powered by Gemini 2.5 Pro & GitHub Actions
        </div>
    </body>
    </html>
    """
    
    # Write to docs/index.html
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_html_digest()
