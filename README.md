# Daily PA

Your automated daily personal assistant powered by Google Gemini 2.5 Pro and GitHub Actions.

Every morning at **6am Dublin time** (5am UTC), this repository wakes up, makes live searches via Gemini for your custom prompts, generates an HTML digest, and publishes it to GitHub Pages.

---

## 🚀 One-Time Setup Instructions

Since this repository is now on your machine, you need to push it to a new GitHub repository to activate the web page and the daily cron job.

### 1. Create the Repo
1. Go to [github.com/new](https://github.com/new)
2. Repository name: `DailyPA`
3. Visibility: **Public** (required for free GitHub Pages)
4. Do NOT check "Add a README" (keep it completely empty)
5. Click **Create repository**

### 2. Push this Code
Open your terminal inside the `DailyPA` folder on your laptop and run:
```bash
git init
git add .
git commit -m "Initial commit for DailyPA"
git branch -M main
git remote add origin https://github.com/vinay-sowdri/DailyPA.git
git push -u origin main
```

### 3. Add your Gemini API Key Secret
The GitHub Action needs your Gemini API key to run.
1. Go to your new repo on GitHub: `https://github.com/vinay-sowdri/DailyPA`
2. Click **Settings** (top right tab)
3. On the left sidebar, go to **Secrets and variables** -> **Actions**
4. Click **New repository secret**
5. Name: `GEMINI_API_KEY`
6. Secret: *(paste your API key from [Google AI Studio](https://aistudio.google.com/apikey))*
7. Click **Add secret**

### 4. Enable GitHub Pages
This makes your daily HTML available as a website.
1. In your repo, go to **Settings**
2. On the left sidebar, click **Pages**
3. Under *Build and deployment*:
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: Select **`/docs`** instead of `/(root)`
4. Click **Save**

### 5. Run it for the first time!
You don't have to wait until tomorrow at 6am to see it work.
1. In your repo, click the **Actions** tab at the top.
2. Under "Workflows" on the left, click **Daily PA Digest**.
3. On the right, click the **Run workflow** dropdown, and click the green **Run workflow** button.
4. Wait about ~45-60 seconds for the job to finish. It will call Gemini and build today's digest!

### 🎉 Access your App
Once the workflow finishes and GitHub Pages builds it, your Daily Assistant is live at:
**`https://vinay-sowdri.github.io/DailyPA/`**

Bookmark this URL on your phone or computer. It will automatically reflect the newest info every morning.

---

## ⚙️ How it works
- `scripts/generate_digest.py`: The Python brain. Sends your 5 prompts to Gemini 2.5 Pro (using Google Search grounding for real-time news/prices), formats the response into HTML, and saves it to `docs/index.html`.
- `scripts/verse_tracker.json`: Tracks which Bhagavad Gita chapter and verse you are on. Automatically increments each successful run.
- `.github/workflows/daily-digest.yml`: The alarm clock. Wakes up at 5am UTC, installs Python, runs the script above, and commits the result back to `main`.
