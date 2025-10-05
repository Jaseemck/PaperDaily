# daily_job.py
import os
os.environ["EMAIL_ADDRESS"] = "jcgesturesbot@gmail.com"
os.environ["EMAIL_PASSWORD"] = "bcxqduqqysqbivns"

from app import send_daily_papers
send_daily_papers()