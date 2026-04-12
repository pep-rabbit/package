from litestar import Litestar
from src.endpoin import router

app = Litestar(route_handlers=[router])