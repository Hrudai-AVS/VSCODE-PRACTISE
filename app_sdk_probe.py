from dotenv import load_dotenv
import os
import inspect
import time

load_dotenv()

def mask(s: str) -> str:
    if not s:
        return "(missing)"
    if len(s) <= 8:
        return s[:2] + "..." + s[-2:]
    return s[:4] + "..." + s[-4:]

def probe_langfuse():
    try:
        import langfuse
    except Exception as e:
        print("langfuse import failed:", e)
        return

    print("Imported langfuse version:", getattr(langfuse, '__version__', '(unknown)'))
    members = dir(langfuse)
    interesting = [m for m in members if any(k in m.lower() for k in ('client','langfuse','init','configure'))]
    print("Interesting members:", interesting)

    # Try to find a Client-like object
    Client = None
    for name in ('Client','Langfuse','LangfuseClient','create_client'):
        if hasattr(langfuse, name):
            Client = getattr(langfuse, name)
            print(f"Found candidate: {name}")
            break

    # If not found, look for callables that may construct a client
    if Client is None:
        for name in members:
            if callable(getattr(langfuse, name)) and ('client' in name.lower() or 'create' in name.lower()):
                Client = getattr(langfuse, name)
                print(f"Found callable candidate: {name}")
                break

    secret = os.getenv('LANGFUSE_SECRET_KEY')
    base = os.getenv('LANGFUSE_BASE_URL')

    print('Base:', base or '(missing)')
    print('Secret:', mask(secret))

    if Client is None:
        print('No obvious client constructor found. Showing dir(langfuse) instead.')
        print('\n'.join(members))
        return

    # Try to instantiate the client with common kwarg names
    kwargs_list = [
        {'api_key': secret},
        {'secret_key': secret},
        {'api_key': secret, 'base_url': base},
        {'secret': secret, 'base_url': base},
        { 'key': secret },
    ]

    client = None
    for kwargs in kwargs_list:
        try:
            c = Client(**{k: v for k, v in kwargs.items() if v})
            client = c
            print('Client instantiated with', kwargs)
            break
        except TypeError:
            continue
        except Exception as e:
            print('Instantiation error with', kwargs, str(e))

    if client is None:
        print('Could not instantiate client with common kwargs; attempting no-arg constructor')
        try:
            client = Client()
            print('Client instantiated with no args')
        except Exception as e:
            print('No-arg instantiation failed:', e)
            return

    # Look for a method to send or track events
    send_methods = [m for m in dir(client) if any(k in m.lower() for k in ('send','log','track','ingest','event'))]
    print('Client send-like methods:', send_methods)

    payload = {'name': 'probe.event', 'timestamp': int(time.time()), 'properties': {'probe': True}}

    for m in send_methods:
        try:
            fn = getattr(client, m)
            if callable(fn):
                print(f'Trying {m}...')
                try:
                    res = fn(payload)
                    print('Called', m, 'result:', res)
                    return
                except TypeError:
                    # maybe separate args
                    try:
                        res = fn(payload['name'], payload)
                        print('Called', m, 'with (name,payload):', res)
                        return
                    except Exception as e:
                        print('Call failed for', m, e)
                except Exception as e:
                    print('Call failed for', m, e)
        except Exception as e:
            print('Error accessing method', m, e)

    print('Probe finished — client present but no send method worked.')

if __name__ == '__main__':
    probe_langfuse()
