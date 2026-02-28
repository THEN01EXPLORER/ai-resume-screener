import re
def validate_pdf_magic_bytes(file_content: bytes) -> bool:
    """
    Checks if the raw binary starts with the Hex signature 25 50 44 46 (%PDF).
    Blocks malware disguised with a .pdf extension.
    """

    return file_content.startswith(b'%PDF')

def clean_extracted_text(text: str) -> str:
    """
    Removes excessive whitespace and common OCR artifacts.
    """
    # Replace multiple spaces/tabs with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Replace multiple newlines with a maximum of two (for paragraph breaks)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()