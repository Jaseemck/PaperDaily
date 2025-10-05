from flask import Flask, request, render_template_string
import feedparser, random, ssl, os, json, re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Load environment variables
load_dotenv()
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
SUBSCRIBER_FILE = "subscribers.json"

JOURNALS = [
    {"name": "Artificial Intelligence", "rss": "https://export.arxiv.org/rss/cs.AI"},
    {"name": "Machine Learning", "rss": "https://export.arxiv.org/rss/cs.LG"},
    {"name": "Computation and Language (NLP)", "rss": "https://export.arxiv.org/rss/cs.CL"},
    {"name": "Computer Vision", "rss": "https://export.arxiv.org/rss/cs.CV"},
    {"name": "Databases", "rss": "https://export.arxiv.org/rss/cs.DB"},
    {"name": "Information Retrieval", "rss": "https://export.arxiv.org/rss/cs.IR"},
    {"name": "Cryptography and Security", "rss": "https://export.arxiv.org/rss/cs.CR"},
    {"name": "Computational Finance", "rss": "https://export.arxiv.org/rss/q-fin.CP"},
    {"name": "Generative AI (GenAI)", "rss": "https://export.arxiv.org/rss/cs.LG"},
    {"name": "Blockchain", "rss": "https://export.arxiv.org/rss/cs.CR"},
    {"name": "Big Data", "rss": "https://export.arxiv.org/rss/cs.DB"},
]

def load_subscribers():
    try:
        with open(SUBSCRIBER_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_subscriber(email, subject_idxs):
    subscribers = load_subscribers()
    for sub in subscribers:
        if sub['email'] == email:
            sub['subject_idxs'] = subject_idxs
            break
    else:
        subscribers.append({"email": email, "subject_idxs": subject_idxs})
    with open(SUBSCRIBER_FILE, "w") as f:
        json.dump(subscribers, f, indent=2)

def fetch_random_paper(subject_idx=None, weekend=False):
    if weekend:
        journal = {
            "name": "TechCrunch Startups (Weekend Special)",
            "rss": "https://techcrunch.com/startups/feed/"
        }
    else:
        if subject_idx is None:
            journal = random.choice(JOURNALS)
        else:
            journal = JOURNALS[subject_idx]
    print(f"Fetching from: {journal['name']} ({journal['rss']})")
    feed = feedparser.parse(journal["rss"])
    print(f"Feed status: {getattr(feed, 'status', 'N/A')}")
    print(f"Feed bozo: {feed.bozo}")
    if feed.bozo:
        print(f"Feed bozo_exception: {feed.bozo_exception}")
    print(f"Fetched {len(feed.entries)} entries.")
    if not feed.entries:
        return {
            "title": "No articles found",
            "link": "#",
            "summary": "No articles are currently available. The source site may be under maintenance or temporarily empty. We'll get back to you with a paper or article the next day as the schedule runs again.",
            "journal": journal["name"]
        }
    entry = random.choice(feed.entries)
    return {
        "title": entry.title,
        "link": entry.link,
        "summary": ("<b>Weekend Special:</b> " if weekend else "") + entry.summary,
        "journal": journal["name"]
    }

def extract_abstract(summary):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', summary).strip()
    abstract_split = cleantext.split("Abstract:", 1)
    return abstract_split[1].strip() if len(abstract_split) == 2 else cleantext

def send_email(to_email, paper):
    msg = MIMEMultipart("alternative")
    msg['Subject'] = "Your Read for the Day 📚"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    abstract = extract_abstract(paper['summary'])

    weekend_label = ""
    if paper.get("weekend"):
        weekend_label = '<div style="color:#e67e22;font-weight:bold;margin-bottom:10px;">🌟 Weekend Special</div>'

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        {weekend_label}
        <h2 style="color: #2c3e50;">{paper['title']}</h2>
        <p><strong>Domain:</strong> {paper['journal']}</p>
        <p><a href="{paper['link']}" style="color: #2980b9;">🔗 Read the full paper</a></p>
        <h3>Abstract</h3>
        <p>{abstract}</p>
        <hr>
        <p style="font-size: 0.9em; color: #7f8c8d;">
            You're receiving this because you subscribed to Daily IT Papers.
            <br><a href="http://localhost:5000/update?email={to_email}">Update preferences</a>
        </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

@app.route('/')
def home():
    return render_template_string('''
    <html>
    <head>
        <title>Subscribe to Daily IT Papers</title>
        <style>
            body { background: #f4f6fa; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; }
            .container { max-width: 440px; margin: 48px auto; background: #fff; border-radius: 14px; box-shadow: 0 4px 24px #e0e0e0; padding: 36px 32px; }
            h2 { color: #2c3e50; margin-bottom: 24px; }
            label { font-weight: 600; margin-bottom: 8px; display: block; }
            .checkbox-group { margin-bottom: 22px; }
            .checkbox-group label { font-weight: 400; margin: 8px 0 0 0; display: flex; align-items: center; }
            .checkbox-group input[type=checkbox] { margin-right: 10px; accent-color: #2980b9; }
            input[type=email] { width: 100%; padding: 10px; margin-bottom: 22px; border-radius: 7px; border: 1px solid #bfc9d1; font-size: 1em; }
            button { background: #2980b9; color: #fff; border: none; padding: 12px 0; border-radius: 7px; font-size: 1.1em; width: 100%; font-weight: 600; cursor: pointer; transition: background 0.2s; }
            button:hover { background: #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Subscribe to Daily IT Papers</h2>
            <form method="POST" action="/subscribe">
                <label for="email">Your Email</label>
                <input type="email" name="email" id="email" placeholder="you@example.com" required>
                <label>Select Domains</label>
                <div class="checkbox-group">
                    {% for idx, journal in journals %}
                        <label>
                            <input type="checkbox" name="domain" value="{{idx}}">
                            {{journal['name']}}
                        </label>
                    {% endfor %}
                </div>
                <button type="submit">Subscribe</button>
            </form>
        </div>
    </body>
    </html>
    ''', journals=list(enumerate(JOURNALS)))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    subject_idxs = [int(idx) for idx in request.form.getlist('domain')]
    save_subscriber(email, subject_idxs)
    chosen_idx = random.choice(subject_idxs)
    paper = fetch_random_paper(chosen_idx)
    send_email(email, paper)
    selected_journals = ', '.join([JOURNALS[idx]['name'] for idx in subject_idxs])
    return render_template_string('''
    <html>
    <head>
        <title>Subscribed!</title>
        <style>
            body { background: #f4f6fa; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; }
            .container { max-width: 440px; margin: 48px auto; background: #fff; border-radius: 14px; box-shadow: 0 4px 24px #e0e0e0; padding: 36px 32px; text-align: center; }
            h2 { color: #27ae60; margin-bottom: 18px; }
            p { color: #2c3e50; }
            a { color: #2980b9; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Subscribed!</h2>
            <p>{{email}}, you will receive papers from: <b>{{journals}}</b></p>
            <a href="/">Back</a>
        </div>
    </body>
    </html>
''', email=email, journals=selected_journals)

@app.route('/update', methods=['GET'])
def update_form():
    email = request.args.get('email')
    subscribers = load_subscribers()
    subscriber = next((s for s in subscribers if s['email'] == email), None)
    if not subscriber:
        return f"No subscription found for {email}.", 404
    return render_template_string('''
    <html>
    <head>
        <title>Update Preferences</title>
        <style>
            body { background: #f4f6fa; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; }
            .container { max-width: 440px; margin: 48px auto; background: #fff; border-radius: 14px; box-shadow: 0 4px 24px #e0e0e0; padding: 36px 32px; }
            h2 { color: #2c3e50; margin-bottom: 24px; }
            label { font-weight: 600; margin-bottom: 8px; display: block; }
            .checkbox-group { margin-bottom: 22px; }
            .checkbox-group label { font-weight: 400; margin: 8px 0 0 0; display: flex; align-items: center; }
            .checkbox-group input[type=checkbox] { margin-right: 10px; accent-color: #2980b9; }
            button { background: #2980b9; color: #fff; border: none; padding: 12px 0; border-radius: 7px; font-size: 1.1em; width: 100%; font-weight: 600; cursor: pointer; transition: background 0.2s; }
            button:hover { background: #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Update Your Preferences</h2>
            <form method="POST" action="/update">
                <input type="hidden" name="email" value="{{email}}">
                <div class="checkbox-group">
                    {% for idx, journal in journals %}
                        <label>
                            <input type="checkbox" name="domain" value="{{idx}}" {% if idx in selected %}checked{% endif %}>
                            {{journal['name']}}
                        </label>
                    {% endfor %}
                </div>
                <button type="submit">Update</button>
            </form>
        </div>
    </body>
    </html>
''', email=email, journals=list(enumerate(JOURNALS)), selected=subscriber['subject_idxs'])

@app.route('/update', methods=['POST'])
def update_subscription():
    email = request.form['email']
    subject_idxs = [int(idx) for idx in request.form.getlist('domain')]
    save_subscriber(email, subject_idxs)
    updated_journals = ', '.join([JOURNALS[idx]['name'] for idx in subject_idxs])
    return render_template_string('''
    <html>
    <head>
        <title>Preferences Updated!</title>
        <style>
            body { background: #f4f6fa; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; }
            .container { max-width: 440px; margin: 48px auto; background: #fff; border-radius: 14px; box-shadow: 0 4px 24px #e0e0e0; padding: 36px 32px; text-align: center; }
            h2 { color: #27ae60; margin-bottom: 18px; }
            p { color: #2c3e50; }
            a { color: #2980b9; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Preferences Updated!</h2>
            <p>{{email}}, your new selection includes: <b>{{journals}}</b></p>
            <a href="/">Back to Home</a>
        </div>
    </body>
    </html>
''', email=email, journals=updated_journals)

def send_daily_papers():
    print(f"📬 Running daily scheduler at {datetime.now()}")
    subscribers = load_subscribers()
    today = datetime.now().weekday()  # 0=Monday, ..., 5=Saturday, 6=Sunday
    weekend = today in [5, 6]
    for sub in subscribers:
        email = sub['email']
        subject_idxs = sub['subject_idxs']
        if weekend:
            paper = fetch_random_paper(weekend=True)
        elif subject_idxs:
            chosen_idx = random.choice(subject_idxs)
            paper = fetch_random_paper(chosen_idx)
        else:
            continue
        send_email(email, paper)

scheduler = BackgroundScheduler()
'''
scheduler.add_job(
    send_daily_papers,
    'cron',
    hour=7,
    minute=0,
    day_of_week='mon-sun'  # Run every day
)
'''
scheduler.add_job(
    send_daily_papers,
    'interval',
    minutes=1
)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
