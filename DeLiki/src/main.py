from litestar import Litestar
from litestar.config.cors import CORSConfig
from src.endpoin import router

app = Litestar(
    route_handlers=[router],
    cors_config=CORSConfig(allow_origins=["*"])
)