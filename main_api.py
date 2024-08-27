from prometheus_fastapi_instrumentator import Instrumentator
from fastapi_utils.inferring_router import InferringRouter
from fastapi.middleware.cors import CORSMiddleware 
from fastapi import FastAPI, File, UploadFile, Request
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import uvicorn
import warnings


from helpers import get_SRL, get_SRL_sentence, get_ThamQuyen, get_ChuDe, refine_data
from Utils.DataHelper.SparkAccess import SparkAccess
from Utils.DataHelper.SupportData import SupportData
from Utils.LoggingHelper import initialize_logging

import config


warnings.filterwarnings("ignore")
# -----------------------------------------------------------------------------------------------
# Lifespan Events
# -----------------------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_logging()
    logging.info("System starting up...")
    # logging.info("Khởi tạo Spark...")
    # spark_acc = SparkAccess()
    # spark_acc.initialize()

    logging.info("Khởi tạo Neo4J KG")
    support_data = SupportData()
    support_data.initialize()
    logging.info("System startup completed.")

    yield
    # logging.info("Spark shutting down...")
    # spark_acc.getSpark().sparkContext.stop()
    logging.info("System shutdown completed.")


# -----------------------------------------------------------------------------------------------
# REST API Initialization
# -----------------------------------------------------------------------------------------------
instrumentator = Instrumentator()
router = InferringRouter()
app = FastAPI(
    title="CLS SRL API",
    description="API cho service SRL/NLP của CLS AI Service",
    version="2.3.0",
    docs_url='/docs/nlp/srl',
    openapi_url='/docs/nlp/srl.json',
    lifespan=lifespan,
)
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
instrumentator.instrument(app).expose(app)


# -----------------------------------------------------------------------------------------------
# Middlewares
# -----------------------------------------------------------------------------------------------
# @app.middleware("http")
# async def unicode_formalize_and_process_time(request: Request, call_next):
#     # request.body = unicodedata.normalize("NFC", request.body)
#     start_time = datetime.now()
#     response = await call_next(request)
#     process_time = datetime.now() - start_time
#     response.headers["X-Process-Time"] = str(process_time.total_seconds())
#     return response






# -----------------------------------------------------------------------------------------------
# API Implementation -- [TODO]: Refactor lại theo kiểu status - message - data
# -----------------------------------------------------------------------------------------------
@router.get("/") # giống flask, khai báo phương thức get và url
def root(): # do dùng ASGI nên ở đây thêm async, nếu bên thứ 3 không hỗ trợ thì bỏ async đi
    return {"msg": "Đối với tôi, đây là một phương pháp tạo hình cực kỳ độc đáo. Nó là thứ gì đó có thể tạo nên một cuộc cách mạng trong hội họa. Vẽ (bắn) lên tường những bức tranh thế này đòi hỏi kỹ năng và sự kiên nhẫn đến mức tối đa. Bất cứ ai khi nhìn vào những tác phẩm này đều rất thán phục người nghệ sĩ đơn giản vì mỗi viên đạn đều được BẮN SÁT NGƯỜI CỦA ĐỐI THỦ mà KHÔNG GÂY RA MỘT DAMAGE NÀO. Tất cả những yếu tố này đều thể hiện kỹ năng SẤY và BÁN CƠM tuyệt vời của một người nghệ sĩ."}


@router.post("/srl/file")
def SRL_file(file: UploadFile = File(...)):
    start_time = datetime.now()
    data = get_SRL(file)
    end_time = datetime.now()

    logging.info(f"Thời gian xử lý: {(end_time - start_time)}s")
    
    if data is None:
        return {"status": "Not Process!", "data": None}
    return {"data": (data.to_dict(orient='records'))}


@router.post("/srl/sentences")
def getSRL_sen(input: dict):

    sentences = input['input']
    rs = get_SRL_sentence(sentences)
    return {"result": (rs)}


@router.post("/srl/tham_quyen/file")
def getSRL_thamquyen(file: UploadFile = File(...)):
    start_time = datetime.now()
    data = get_ThamQuyen(file)
    end_time = datetime.now()

    logging.info(f"Thời gian xử lý: {(end_time - start_time)}s")
    
    if data is None:
        return {"status": "Not Process!", "data": None}
    return {"data": (data.to_dict(orient='records'))}


@router.post("/srl/chu_de/file")
def getSRL_thamquyen(file: UploadFile = File(...)):
    start_time = datetime.now()
    data = get_ChuDe(file)
    end_time = datetime.now()

    logging.info(f"Thời gian xử lý: {(end_time - start_time)}s")
    
    if data is None:
        return {"status": "Not Process!", "data": None}
    return {"data": (data.to_dict(orient='records'))}


@router.post("/srl/refine_only/file")
def refine_ocr_data(file: UploadFile = File(...)):
    start_time = datetime.now()
    data = refine_data(file)
    end_time = datetime.now()

    logging.info(f"Thời gian xử lý: {(end_time - start_time)}s")
    
    if data is None:
        return {"status": "Not Process!", "data": None}
    return {"data": (data.to_dict(orient='records'))}


 


# -----------------------------------------------------------------------------------------------
# App Deployment
# -----------------------------------------------------------------------------------------------
app.include_router(router)
if __name__ == '__main__':
    uvicorn.run('main_api:app', host='0.0.0.0', port=8007, reload=True, workers=4)


