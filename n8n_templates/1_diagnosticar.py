python -c "
import json
with open('erros_finais.json') as f:
    erros = json.load(f)
from collections import Counter
msgs = Counter(e['erro'][:70] for e in erros)
for msg, count in msgs.most_common():
    print(f'{count}x: {msg}')
"