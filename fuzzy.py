import re

# Abc -> Abc = 10
# abc -> Abc = 9
# Abc -> abc = 9
# B a -> a B = 8
# b a -> a b = 7
# ab -> acb = 4
# x -> ab = 0

MAX_SCORE = 1000

def score(text, query):
    if query in text:
        return MAX_SCORE
    text_lower = text.lower()
    if query in text_lower:
        return 999
    if query.lower() in text_lower:
        return 998
    query_split = query.split(' ')
    if all(word in text for word in query_split):
        return 900
    query_split_lower = query.lower().split(' ')
    if all(word in text_lower for word in query_split_lower):
        return 889
    query_pattern = re.compile('.*' + '.*'.join(re.escape(l) for l in query) + '.*')
    if query_pattern.match(text):
        return 500
    return 0


def filter(texts, query, key=lambda x: x):
    texts_with_score = ((score(key(t), query), t) for t in texts)
    sorted_texts_with_score = sorted(texts_with_score, reverse=True)
    print(sorted_texts_with_score)
    return tuple(t for (score, t) in sorted_texts_with_score if score > 0)