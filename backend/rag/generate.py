import re
from transformers import pipeline
import torch

# Check if GPU is available
device = 0 if torch.cuda.is_available() else -1
print(f"🎮 Using device: {'GPU (CUDA)' if device == 0 else 'CPU'}")

llm = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    max_length=512,
    min_length=100,
    do_sample=False,
    truncation=True,
    device=device
)


def clean_repetition(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    seen = set()
    cleaned = []

    for s in sentences:
        key = re.sub(r"[^\w\s]", "", s.lower())
        if key not in seen:
            seen.add(key)
            cleaned.append(s)

    return " ".join(cleaned)


def generate(question, context):
    if not context:
        return "I am not confident enough to answer this question based on the available documents."

    prompt = f"""
You are NLPAssist+, an educational AI assistant.

Answer the question using the information from the context below. Your answer should:
- Be comprehensive and informative
- Use specific details from the context
- Provide a complete explanation (aim for 5-8 sentences)
- Stay on topic and directly address what was asked
- Not mention RAG or retrieval systems unless the question asks about them

Context:
{' '.join(context)}

Question:
{question}

Answer:
"""

    raw = llm(prompt)[0]["generated_text"]
    answer = clean_repetition(raw).strip()
    
    # DEBUG
    print(f"\n=== GENERATION DEBUG ===")
    print(f"Question: {question}")
    print(f"Raw output: {raw}")
    print(f"After clean: {answer}")
    print(f"Words: {len(answer.split())}")
    print("======================\n")
    
    if len(answer.split()) < 8:
        return "I am not confident enough to answer this question based on the available documents."

    if "rag" not in question.lower():
        answer = re.sub(
            r"retrieval[- ]augmented generation.*?$",
            "",
            answer,
            flags=re.IGNORECASE
        ).strip()

    return answer
