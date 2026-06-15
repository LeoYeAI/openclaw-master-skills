import sys
import json

def safe_get(data, keys):
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        elif isinstance(data, list) and key.isdigit() and int(key) < len(data):
            data = data[int(key)]
        else:
            return None
    return data

if __name__ == "__main__":
    if len(sys.argv) > 1:
        keys = sys.argv[1].split('.')
        try:
            input_data = json.load(sys.stdin)
            result = safe_get(input_data, keys)
            if result is not None:
                print(json.dumps(result))
        except json.JSONDecodeError:
            pass
