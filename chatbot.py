import PyPDF2
import time
from groq import Groq
# Assuming your config file exists with these variables
from config import API_KEY, MODEL 

client = Groq(api_key=API_KEY)

# --- OPTIMIZED SETTINGS ---
# Smaller chunks + higher TOP_CHUNKS = better "vision" across a long PDF
CHUNK_SIZE = 3000   # ~750 tokens
OVERLAP    = 400    
TOP_CHUNKS = 12     # Increased: Sends 12 different parts of the PDF to Groq
MAX_TOKENS = 12000  # Adjust based on your Groq model's limit (e.g., Llama 3 70b)

def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    chunks = []
    start  = 0
    index  = 1
    # Estimate total for the tag
    total = (len(text) // (size - overlap)) + 1

    while start < len(text):
        end   = start + size
        chunk = f"[Section {index} (Approx Page {max(1, index//2)})]\n" + text[start:end]
        chunks.append(chunk)
        start += size - overlap
        index += 1
    return chunks

def _spread_chunks(chunks: list[str], n: int) -> list[str]:
    """Retrieves n chunks distributed evenly across the entire document."""
    if len(chunks) <= n:
        return chunks
    step = len(chunks) / n
    selected = [chunks[int(i * step)] for i in range(n)]
    return selected

def _rank_chunks(chunks: list[str], query: str, top_n: int = TOP_CHUNKS) -> list[str]:
    STOP_WORDS = {"the", "a", "an", "is", "are", "to", "of", "in", "and", "or", "for"}
    
    # Check if user wants a general overview
    summary_terms = ["summary", "summarize", "overview", "about", "whole", "entire", "all"]
    is_general = any(term in query.lower() for term in summary_terms)
    
    if is_general:
        # If asking a general question, skip keywords and look at the whole PDF
        return _spread_chunks(chunks, top_n)

    query_words = [w.lower().strip(".,?!") for w in query.split() if w.lower() not in STOP_WORDS]
    
    scored = []
    for i, chunk in enumerate(chunks):
        score = 0
        lower_chunk = chunk.lower()
        for word in query_words:
            if word in lower_chunk:
                score += 3 if f" {word} " in lower_chunk else 1
        scored.append((score, i, chunk))

    scored.sort(key=lambda x: (-x[0], x[1]))
    
    # If no keywords found, fallback to spreading across document
    if scored[0][0] == 0:
        return _spread_chunks(chunks, top_n)

    top = scored[:top_n]
    top.sort(key=lambda x: x[1]) # Keep chronological order
    return [c for _, _, c in top]

class PDFChatBot:
    def __init__(self):
        self.pdf_chunks    = []
        self.pdf_name      = None
        self.chat_history  = []
        self.total_pages   = 0

    def upload_pdf(self, pdf_path: str) -> tuple[bool, str]:
        try:
            print(f"Loading {pdf_path}...")
            text = ""
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                self.total_pages = len(reader.pages)
                for i, page in enumerate(reader.pages):
                    extracted = page.extract_text()
                    if extracted:
                        text += f"\n[DOC PAGE {i+1}]\n{extracted}\n"
            
            if not text.strip():
                return False, "No text found in PDF."

            self.pdf_chunks = _chunk_text(text)
            self.pdf_name = pdf_path.split("/")[-1]
            print(f"Processed {self.total_pages} pages into {len(self.pdf_chunks)} sections.")
            return True, f"Loaded {self.total_pages} pages."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def send_message(self, user_input: str) -> str:
        if not self.pdf_chunks:
            return "Please upload a PDF."

        # Get relevant context (Keyword search OR Full-doc spread)
        relevant_sections = _rank_chunks(self.pdf_chunks, user_input, TOP_CHUNKS)
        context = "\n\n---\n\n".join(relevant_sections)

        system_prompt = f"""You are analyzing '{self.pdf_name}'. 
Below are {len(relevant_sections)} selected sections from the document to help you answer.
If the answer isn't in these sections, say you can't find it but mention what you DID see.

--- DOCUMENT DATA ---
{context}
--- END DATA ---"""

        messages = [{"role": "system", "content": system_prompt}]
        for u, a in self.chat_history[-4:]:
            messages.append({"role": "user", "content": u})
            messages.append({"role": "assistant", "content": a})
        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.1 # Keep it strictly factual
            )
            reply = response.choices[0].message.content
            self.chat_history.append((user_input, reply))
            return reply
        except Exception as e:
            return f"API Error: {str(e)}"

# --- QUICK TEST ---
if __name__ == "__main__":
    bot = PDFChatBot()
    # bot.upload_pdf("your_file.pdf")
    # print(bot.send_message("What is the summary of the whole document?"))