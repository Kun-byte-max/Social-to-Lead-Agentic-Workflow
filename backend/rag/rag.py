import json

KNOWLEDGE_CHUNKS = [
    "Basic Plan pricing is $29/month. Includes 10 videos/month and 720p resolution.",
    "Pro Plan pricing is $79/month. Includes Unlimited videos, 4K resolution, and AI captions.",
    "Policy: No refunds after 7 days.",
    "Policy: 24/7 support available only on Pro plan."
]

def retrieve_knowledge(query: str) -> list[str]:
    retrieved = []
    q = query.lower()
    
    for chunk in KNOWLEDGE_CHUNKS:
        if "pro" in q and "pro" in chunk.lower():
            retrieved.append(chunk)
        elif "basic" in q and "basic" in chunk.lower():
            retrieved.append(chunk)
        elif "refund" in q and "refund" in chunk.lower():
            retrieved.append(chunk)
        elif "support" in q and "support" in chunk.lower():
            retrieved.append(chunk)
        elif "price" in q or "cost" in q or "pricing" in q:
            if "pricing" in chunk:
                retrieved.append(chunk)
    
    if not retrieved:
        retrieved = KNOWLEDGE_CHUNKS 
        
    return retrieved
