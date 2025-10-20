from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from src.services import pdf_service
from src.utils.file_utils import save_upload_file, cleanup_temp_files, remove_file
import tempfile
from typing import List

router = APIRouter(prefix="/pdf")


@router.post("/merge")
async def merge_pdfs(
    background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)
):
    paths = [await save_upload_file(f) for f in files]
    output_path = tempfile.mktemp(suffix=".pdf")
    try:
        await pdf_service.merge_pdfs(paths, output_path)
        cleanup_temp_files(*paths)
        background_tasks.add_task(remove_file, output_path)
        return FileResponse(
            output_path, filename="merged.pdf", media_type="application/pdf"
        )
    except Exception as e:
        cleanup_temp_files(output_path, *paths)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/split")
async def split_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    start: int = Form(1),
    end: int | None = Form(None),
):
    input_path = await save_upload_file(file)
    output_path = tempfile.mktemp(suffix=".pdf")
    try:
        await pdf_service.split_pdf(input_path, output_path, start, end)
        background_tasks.add_task(remove_file, output_path)
        return FileResponse(
            output_path, filename="split.pdf", media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_temp_files(input_path)


@router.post("/extract-text")
async def extract_text(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    input_path = await save_upload_file(file)
    output_path = tempfile.mktemp(suffix=".txt")
    try:
        await pdf_service.extract_text(input_path, output_path)
        background_tasks.add_task(remove_file, output_path)
        return FileResponse(output_path, filename="text.txt", media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_temp_files(input_path)


@router.post("/to-pdf")
async def convert_to_pdf(
    background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)
):
    """
    Конвертирует несколько файлов (например, изображения, TXT) в единый PDF.
    """
    paths = [await save_upload_file(f) for f in files]
    output_path = tempfile.mktemp(suffix=".pdf")

    try:
        await pdf_service.convert_to_pdf(paths, output_path)
        cleanup_temp_files(*paths)
        background_tasks.add_task(remove_file, output_path)
        return FileResponse(
            output_path, filename="converted.pdf", media_type="application/pdf"
        )
    except Exception as e:
        cleanup_temp_files(output_path, *paths)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compress")
async def compress_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Сжимает PDF реальным уменьшением изображений.
    """
    input_path = await save_upload_file(file)
    output_path = tempfile.mktemp(suffix=".pdf")

    try:
        await pdf_service.compress_pdf(input_path, output_path)
        background_tasks.add_task(remove_file, output_path)
        return FileResponse(
            output_path, filename="compressed.pdf", media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_temp_files(input_path)
