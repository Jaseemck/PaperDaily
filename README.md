# BigData Daily

A Flask web app that emails you a daily research paper or article from your chosen IT domains (AI, ML, Big Data, Blockchain, etc.) using arXiv RSS feeds. On weekends, you’ll receive a “Weekend Special” startup article from TechCrunch.

## Features

- Subscribe with your email and select multiple IT domains.
- Receive a daily email with a random paper from your chosen domains (Mon–Fri).
- On weekends, receive a “Weekend Special” article from TechCrunch Startups.
- Update your preferences anytime via a link in your email.
- Scheduler runs automatically and sends emails to all subscribers.

## Tech Stack

- Python, Flask
- APScheduler (for scheduling daily emails)
- feedparser (for parsing RSS feeds)
- gunicorn (for production server)
- dotenv (for environment variables)

## Setup & Deployment

### Local Development

1. **Clone the repo:**
    ```sh
    git clone https://github.com/yourusername/bigdata-daily.git
    cd bigdata-daily
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # or
    source venv/bin/activate  # On Mac/Linux
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    - Create a `.env` file with:
      ```
      EMAIL_ADDRESS=your_email@gmail.com
      EMAIL_PASSWORD=your_app_password
      ```

5. **Run the app:**
    ```sh
    python app.py
    ```
    - Visit [http://localhost:5000](http://localhost:5000) to use the web interface.

### Deploying on Render.com

1. Push your code to GitHub.
2. Create a `Procfile`:
    ```
    web: gunicorn app:app
    worker: python app.py
    ```
3. Create a new Web Service and a Background Worker on [Render.com](https://render.com/), both pointing to your repo.
4. Set `EMAIL_ADDRESS` and `EMAIL_PASSWORD` as environment variables in Render’s dashboard.

## How It Works

- **Weekdays:** Each subscriber gets a random paper from their selected arXiv domains.
- **Weekends:** All subscribers get a random startup article from TechCrunch.
- If no papers are available, the email will explain and try again the next day.

## Domains Supported

- Artificial Intelligence
- Machine Learning
- Computation and Language (NLP)
- Computer Vision
- Databases
- Information Retrieval
- Cryptography and Security
- Computational Finance
- Generative AI (GenAI)
- Blockchain
- Big Data

## License

MIT License

---

**Made with ❤️ for daily learning!**