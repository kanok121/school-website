# How to Put This Website Online and Turn It Into an Android App (APK)

This guide is for absolute beginners. Follow the steps in order.

---

## PART A — Put the code on GitHub (needed for hosting)

1. Go to **https://github.com** and click **Sign up** (free). Create an account.
2. Download **GitHub Desktop** from **https://desktop.github.com** and install it.
3. Open GitHub Desktop, sign in with the GitHub account you just created.
4. Click **File → Add Local Repository**.
5. Click **Choose...** and select your `school_website` folder (the one with `app.py` inside).
6. It will say "This directory does not appear to be a Git repository" → click **"create a repository"** (a blue link in that message).
7. Click **Create Repository**.
8. Now click the blue **Publish repository** button (top of the window).
9. Uncheck "Keep this code private" if you don't mind it being public (or keep it private — both work fine for this).
10. Click **Publish Repository**.

Your code is now on GitHub. You can see it by clicking **"View on GitHub"** in the app.

---

## PART B — Host it online for free (Render.com)

1. Go to **https://render.com** and click **Get Started** → sign up using your **GitHub account** (easiest — one click).
2. Once logged in, click **New +** (top right) → **Web Service**.
3. It will show your GitHub repositories — find `school_website` and click **Connect**.
4. Fill in the settings:
   - **Name:** `mojidpur-central-school` (or anything you like — this becomes part of your website address)
   - **Region:** choose the one closest to you (e.g. Singapore)
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free
5. Click **Create Web Service**.
6. Wait 2–5 minutes while it builds. You'll see logs scrolling. When it says "Live" at the top, it's done.
7. Your website address will look like:
   ```
   https://mojidpur-central-school.onrender.com
   ```
   This works from any phone, anywhere, anytime — no computer needed.
8. Log in with `admin` / `admin123` and change nothing yet — test that it works first.

### ⚠️ Important limitation of the free plan
On Render's **free** tier, the server "sleeps" after 15 minutes of no visits (it wakes up again in ~30 seconds the next time someone visits — just a short delay, not a real problem). Also, data saved in the SQLite database **can reset** whenever the app restarts/redeploys, because the free plan's storage isn't permanent. For a small school project this is usually fine to start with — if you later want data to always stay safe permanently, that needs a small paid add-on (I can help set that up when needed).

---

## PART C — Turn the live website into an installable APK

1. Go to **https://www.pwabuilder.com**
2. In the box at the top, paste your Render website address (e.g. `https://mojidpur-central-school.onrender.com`) and click the arrow/Start button.
3. It will scan your site for a few seconds.
4. Click the **Android** icon/package option (may be under a "Package for Stores" or similar button).
5. Keep the default settings and click **Generate** / **Download**.
6. It will download a `.zip` — inside it (or directly) you'll find a `.apk` file (or `.aab` — if you get `.aab`, tell me and I'll explain how to convert it, but `.apk` is what you want for direct install).

### Installing the APK on your phone
1. Copy the `.apk` file to your phone (via USB, or email it to yourself, or upload to Google Drive and download on phone).
2. Tap the file to install.
3. Android will warn "install from unknown sources" — go to **Settings → allow this app to install unknown apps** (Android will show you a button to do this directly when you try to install).
4. Once installed, you'll have an app icon on your phone that opens your school website directly — just like a real app.

---

## Order to do things
1. Part A first (GitHub)
2. Part B second (Render — get your live link)
3. Test the live link works in your phone's browser
4. Part C last (turn that link into an APK)

Go one part at a time and tell me what you see at each step — I'll help if anything looks different from what's described here.
