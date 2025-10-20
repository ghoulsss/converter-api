from PyPDF2 import PdfReader, PdfWriter


async def merge_pdfs(input_files: list[str], output_file: str):
    writer = PdfWriter()
    for path in input_files:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_file, "wb") as f:
        writer.write(f)


async def split_pdf(input_file: str, output_file: str, start: int, end: int | None):
    reader = PdfReader(input_file)
    writer = PdfWriter()
    if not end:
        end = len(reader.pages)
    for i in range(start - 1, end):
        writer.add_page(reader.pages[i])
    with open(output_file, "wb") as f:
        writer.write(f)


async def extract_text(input_file: str, output_file: str):
    reader = PdfReader(input_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
