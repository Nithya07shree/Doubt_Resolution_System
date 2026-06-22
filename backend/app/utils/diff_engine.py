import difflib
import re
from typing import Dict, Any, List

def tokenize(text: str) -> List[str]:
    """
    Splits text into words, punctuation, and spaces to preserve formatting.
    Example: "Hello, world!" -> ['Hello', ',', ' ', 'world', '!']
    """
    return re.findall(r'\w+|[^\w\s]|\s+', text)

def compute_diff(text_a: str, text_b: str) -> Dict[str, Any]:
    """
    Computes a word-by-word diff between two text strings using standard difflib.ndiff.
    Returns metadata about insertions and deletions, alongside unified token chunks.
    """
    if not text_a:
        text_a = ""
    if not text_b:
        text_b = ""

    tokens_a = tokenize(text_a)
    tokens_b = tokenize(text_b)

    # difflib.ndiff returns a delta showing structural comparison
    diff_generator = difflib.ndiff(tokens_a, tokens_b)

    chunks: List[Dict[str, str]] = []
    current_type = None
    current_text: List[str] = []

    words_added = 0
    words_removed = 0

    for item in diff_generator:
        prefix = item[:2]
        token = item[2:]

        # Skip guide markers created by difflib for line details
        if prefix == "? ":
            continue

        # Map prefix code to visual chunk status
        if prefix == "- ":
            chunk_type = "removed"
            if re.match(r'\w+', token):
                words_removed += 1
        elif prefix == "+ ":
            chunk_type = "added"
            if re.match(r'\w+', token):
                words_added += 1
        else:  # "  "
            chunk_type = "equal"

        # Accumulate adjacent tokens of the exact same category
        if chunk_type == current_type:
            current_text.append(token)
        else:
            if current_type is not None:
                chunks.append({
                    "type": current_type,
                    "text": "".join(current_text)
                })
            current_type = chunk_type
            current_text = [token]

    # Flush the last remaining accumulated chunk
    if current_type is not None:
        chunks.append({
            "type": current_type,
            "text": "".join(current_text)
        })

    return {
        "words_added": words_added,
        "words_removed": words_removed,
        "chunks": chunks
    }
