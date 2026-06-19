# Langfuse simple test

This small project reads Langfuse keys from `.env` and posts a test event to common endpoints.

Usage:

1. Ensure your `.env` contains `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_BASE_URL`.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python app.py`

The script will try a few common endpoint paths and print results.
