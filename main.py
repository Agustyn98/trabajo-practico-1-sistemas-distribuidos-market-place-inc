import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, Float, String, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

DATABASE_URL = "sqlite+aiosqlite:///./monolito.db"
engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)
Base = declarative_base()

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    precio = Column(Float)
    stock = Column(Integer)

class PedidoORM(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer)
    total = Column(Float)

class CrearPedidoRequest(BaseModel):
    producto_id: int
    cantidad: int

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Crea las tablas y un producto de prueba si no existe
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Producto).where(Producto.id == 1))
        if not result.scalar_one_or_none():
            session.add(Producto(nombre="Notebook", precio=1000.0, stock=5000))
            await session.commit()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/products")
async def listar_productos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Producto))
    return result.scalars().all()

@app.get("/products/{id}")
async def obtener_producto(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Producto).where(Producto.id == id))
    producto = result.scalar_one_or_none()
    if not producto:
        raise HTTPException(404, "Producto no encontrado")
    return producto

@app.post("/orders", status_code=201)
async def crear_pedido(req: CrearPedidoRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Producto).where(Producto.id == req.producto_id))
    producto = result.scalar_one_or_none()
    
    if not producto:
        raise HTTPException(404, "Producto no encontrado")
    if producto.stock < req.cantidad:
        raise HTTPException(400, "Stock insuficiente")
    
    await asyncio.sleep(3)
    
    producto.stock -= req.cantidad
    db.add(PedidoORM(producto_id=req.producto_id, total=producto.precio * req.cantidad))
    await db.commit()
    
    return {"status": "Pedido creado", "nuevo_stock": producto.stock}