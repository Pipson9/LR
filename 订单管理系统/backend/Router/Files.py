import pathlib
from fastapi.staticfiles import StaticFiles



from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException
# 从 FastAPI 中导入需要使用的组件：
# FastAPI：创建 FastAPI 应用（这里实际上没有使用）
# UploadFile：用于接收上传的文件对象，比普通 bytes 更适合处理大文件
# File：告诉 FastAPI，这个参数来自文件上传
# APIRouter：创建路由模块，用于拆分接口
from pathlib import Path

from db.Models.Products import Product

# 导入 Path 类，用于处理文件路径
# 比如：
# Path("uploads/test.jpg")
# 可以方便地拼接、判断文件是否存在
router = APIRouter(
    prefix="/files",
    tags=["文件管理"],
)
#文件大小限制； 1024 bytes 1024B*1024=1M
MAX_FILE_SIZE=2*1024*1042
ALLOWED_IMAGE_TYPES = {  #文件类型限制
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/jpg",
    "image/gif",
    "image/bmp",
}
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="请上传正确的类型"
        )
    data= await file.read()
    if len(data)>MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="文件太大"
        )
    upload_dir=Path("uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path=upload_dir.joinpath(file.filename)
    file_path.write_bytes(data)
    return {
        'filename': file.filename,
        'content_type': file.content_type,
        'size': file.size
    }



