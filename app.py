from dotenv import load_dotenv
import os
from langfuse import Langfuse

load_dotenv()

def mask(s: str) -> str:
    if not s:
        return "(missing)"
    if len(s) <= 8:
        return s[:2] + "..." + s[-2:]
    return s[:4] + "..." + s[-4:]


def main():
    secret = os.getenv("LANGFUSE_SECRET_KEY")
    public = os.getenv("LANGFUSE_PUBLIC_KEY")
    base = os.getenv("LANGFUSE_BASE_URL")

    print("Langfuse base:", base or "(missing)")
    print("Langfuse public:", mask(public))
    print("Langfuse secret:", mask(secret))

    if not secret or not public or not base:
        print("Missing LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, or LANGFUSE_BASE_URL in .env. Exiting.")
        return

    client = Langfuse(secret_key=secret, public_key=public, base_url=base)
    prompt_text = "what is langfuse"
    response_text = (
        "Langfuse is a platform for capturing prompts, model outputs, events, and traces "
        "from AI applications so you can analyze and debug LLM behavior."
    )

    print("Sending traced prompt to Langfuse...")

    try:
        with client.start_as_current_observation(
            name="Prompt: what is langfuse",
            as_type="generation",
            input={"prompt": prompt_text},
            output={"response": response_text},
            model="langfuse-sdk-test",
            metadata={"source": "python-app"},
        ) as observation:
            print("Observation created:", type(observation).__name__)

        client.flush()
        print("Trace sent successfully. Check Langfuse for the recorded trace.")
    except Exception as exc:
        print("Failed to send prompt trace:", exc)


if __name__ == '__main__':
    main()
