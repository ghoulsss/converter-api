import asyncio
from PyPDF2 import PdfReader, PdfWriter
import os
from PIL import Image
import pikepdf


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


async def convert_to_pdf(input_files: list[str], output_file: str):
    """
    Объединяет изображения (PNG, JPG и т.д.) или конвертируемые форматы в один PDF.
    """
    images = []
    for file_path in input_files:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".png", ".jpg", ".jpeg"]:
            img = Image.open(file_path).convert("RGB")
            images.append(img)
        elif ext == ".pdf":
            # уже PDF, можно просто объединить позднее (в расширенной версии)
            continue
        else:
            raise ValueError(f"Формат {ext} не поддерживается для конвертации")

    if not images:
        raise ValueError("Нет подходящих файлов для создания PDF")

    # сохраняем как многолистовый PDF
    first_image, *rest_images = images
    first_image.save(output_file, save_all=True, append_images=rest_images)


async def compress_pdf(input_file: str, output_file: str, quality: str = "medium"):
    """
    Сжимает PDF за счёт перекодирования потоков изображений и удаления мусора.
    quality — один из вариантов: "screen", "ebook", "printer", "prepress", "default".
    """

    def _compress_sync():
        try:
            # Открытие PDF с доступом к странице
            pdf = pikepdf.open(input_file)

            # Очистка неиспользуемых объектов и пересохранение с фильтрацией
            pdf.save(
                output_file,
                compression=pikepdf.CompressionLevel.default,
                optimize_streams=True,
                linearize=True,
            )
            pdf.close()
        except Exception as e:
            raise RuntimeError(f"Ошибка при сжатии PDF: {e}")

    await asyncio.to_thread(_compress_sync)
