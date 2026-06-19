from dotenv import load_dotenv
import os
import inspect

load_dotenv()

def mask(s: str) -> str:
    if not s:
        return "(missing)"
    if len(s) <= 8:
        return s[:2] + "..." + s[-2:]
    return s[:4] + "..." + s[-4:]

def inspect_client():
    import langfuse
    secret = os.getenv('LANGFUSE_SECRET_KEY')
    base = os.getenv('LANGFUSE_BASE_URL')
    print('Langfuse version:', getattr(langfuse, '__version__', '(unknown)'))
    print('Base:', base)
    print('Secret:', mask(secret))

    # Try get_client first
    client = None
    try:
        if hasattr(langfuse, 'get_client'):
            for kwargs in ({'api_key': secret}, {'secret_key': secret}, {'api_key': secret, 'base_url': base}, {'secret_key': secret, 'base_url': base}):
                try:
                    client = langfuse.get_client(**{k: v for k, v in kwargs.items() if v})
                    print('get_client() succeeded with', kwargs)
                    break
                except Exception as e:
                    print('get_client() failed with', kwargs, e)

    except Exception as e:
        print('get_client call error', e)

    if client is None:
        # Try direct constructor
        Cands = ['Langfuse','Client','LangfuseClient']
        for name in Cands:
            if hasattr(langfuse, name):
                Cl = getattr(langfuse, name)
                try:
                    client = Cl(secret_key=secret, base_url=base)
                    print(f'Instantiated {name} with secret_key,base_url')
                    break
                except Exception as e:
                    try:
                        client = Cl(api_key=secret, api_base=base)
                        print(f'Instantiated {name} with api_key,api_base')
                        break
                    except Exception as e2:
                        print(f'{name} instantiation errors:', e, e2)

    if client is None:
        print('Could not obtain a client instance')
        return

    print('Client type:', type(client))
    attrs = dir(client)
    print('Number of attributes on client:', len(attrs))

    # Print callable attributes and their signatures (limited)
    callables = [a for a in attrs if callable(getattr(client, a)) and not a.startswith('_')]
    print('Public callable attributes:', callables)
    for name in callables:
        try:
            fn = getattr(client, name)
            sig = inspect.signature(fn)
            print(name, 'signature:', sig)
        except Exception as e:
            print('Could not get signature for', name, e)

    # Also show private/send-like methods
    send_like = [a for a in attrs if any(k in a.lower() for k in ('send','create','event','ingest','log','track'))]
    print('Send-like methods (incl. private):', send_like)
    for name in send_like:
        try:
            fn = getattr(client, name)
            print(name, '->', fn)
        except Exception as e:
            print('Error printing', name, e)

if __name__ == '__main__':
    inspect_client()
