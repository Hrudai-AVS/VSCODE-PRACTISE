from dotenv import load_dotenv
import os
import json

load_dotenv()

def mask(s: str) -> str:
    if not s:
        return "(missing)"
    if len(s) <= 8:
        return s[:2] + "..." + s[-2:]
    return s[:4] + "..." + s[-4:]

def send_event():
    import langfuse
    secret = os.getenv('LANGFUSE_SECRET_KEY')
    base = os.getenv('LANGFUSE_BASE_URL')
    print('Langfuse version:', getattr(langfuse, '__version__', '(unknown)'))
    print('Base:', base)
    print('Secret:', mask(secret))

    # Instantiate client similarly to probe
    Client = getattr(langfuse, 'Langfuse', None)
    if Client is None:
        print('Langfuse client class not found')
        return

    client = None
    try:
        client = Client(secret_key=secret, base_url=base)
    except Exception as e:
        try:
            client = Client(api_key=secret, api_base=base)
        except Exception as e2:
            print('Could not instantiate client:', e, e2)
            return

    print('Client created:', type(client))

    try:
        ev = client.create_event(name='probe.event', input={'hello': 'world'}, metadata={'source': 'sdk-send'})
        print('create_event returned:', ev)
    except Exception as e:
        print('create_event failed:', e)

if __name__ == '__main__':
    send_event()
