import aiofiles
import os
import tempfile


async def save_upload_file(upload_file):
    """Сохраняет загруженный файл во временную директорию."""
    suffix = os.path.splitext(upload_file.filename)[1]
    temp_path = tempfile.mktemp(suffix=suffix)
    async with aiofiles.open(temp_path, "wb") as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return temp_path


def cleanup_temp_files(*paths):
    """Удаляет временные файлы."""
    for path in paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass


def remove_file(path: str):
    """Удаляет файл (используется в BackgroundTasks)."""
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass
