"""
Helper script called by detect-secrets.bat
Parses the detect-secrets JSON output and prints results.
Exit code: 0 = clean, 1 = secrets found, 2 = error
"""
import json, sys

try:
    with open('.secrets.new') as f:
        data = json.load(f)
    results = data.get('results', {})
    if results:
        print('  [WARNING] detect-secrets flagged the following:')
        print()
        for fname in results:
            print('  File: ' + fname)
            for hit in results[fname]:
                line = hit.get('line_number', '?')
                kind = hit.get('type', 'unknown')
                print('    -> Line ' + str(line) + ': ' + kind)
        print()
        sys.exit(1)
    else:
        print('  [CLEAN] No secrets found by detect-secrets.')
        sys.exit(0)
except Exception as e:
    print('  [ERROR] Could not parse scan results: ' + str(e))
    sys.exit(2)
