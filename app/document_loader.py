from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
def load_pdf(pdf_path:str):
    loader=PyPDFLoader(pdf_path)
    docs = loader.load()
    filename = Path(pdf_path).name
    for doc in docs:
        doc.metadata["filename"] = filename    
    return docs