import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from app.text_splitter import text_splitter


def load_url(url: str) -> list[Document]:
    """Scrape a URL, clean the text, return chunks ready for ChromaDB."""

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # remove nav, footer, scripts — we only want body content
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # get clean text
    text = soup.get_text(separator="\n")

    # remove blank lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    if not clean_text:
        raise ValueError(f"No content found at URL: {url}")

    # wrap in LangChain Document with metadata
    doc = Document(
        page_content=clean_text,
        metadata={"source": url, "type": "url"}
    )

    # reuse your existing text_splitter
    chunks = text_splitter.split_documents([doc])
    return chunks