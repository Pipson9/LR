from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy import select
from db.Models.Products import Product   # 文件名是 Products.py（大写P），import 要和文件名一致
from db.Models.User import User
from db.database import asyncSession
from dependencies import get_db, get_fenye, get_current_user, get_current_admin   # 引入两个权限依赖
from schemas.product import ProductResponse,ProductCreate,ProductUpdate



router = APIRouter(prefix="/products", tags=["商品管理"])

# 查询商品列表（分页）：登录即可（用户要能浏览商品，所以不能设成仅管理员）
@router.get("/", response_model=list[ProductResponse])
async def query_all(
    current_user: User = Depends(get_current_user),   # 至少要登录，未登录 401
    async_db: asyncSession = Depends(get_db),
    pagination: dict = Depends(get_fenye)   # 分页依赖：从查询参数读 page / page_size，算出 offset

):
    sql = select(Product).offset(pagination["offset"]).limit(pagination["page_size"])

    results = await async_db.execute(sql)
    products = results.scalars().all()
    return products


# 根据id查询商品：登录即可
@router.get("/{id}", response_model=ProductResponse)
async def query_by_id(
    id: int,
    current_user: User = Depends(get_current_user),   # 登录即可
    async_db: asyncSession = Depends(get_db),
):
    sql = select(Product).where(Product.id == id)
    results = await (async_db.execute(sql))
    product = results.scalars().first()
    if product is None:   # 修复原代码 bug：原来写的是 if results is None，results 是 SQLAlchemy Result 对象永远不会是 None，所以查不到商品时不会 404 而是直接 NoneType 崩掉
        raise HTTPException(status_code=404,detail="查询的id不存在")
    return product


# 创建商品：仅管理员（上架商品是运营动作，不能让普通用户自己造商品）
@router.post("/", response_model=ProductResponse)
async def create_product(
       product: ProductCreate,
       current_user: User = Depends(get_current_admin),   # 仅管理员
       async_db: asyncSession = Depends(get_db)):
    new_product = Product(
        name=product.name,
        price=product.price,
        stock=product.stock,
        is_active=product.is_active,
    )
    async_db.add(new_product)
    await async_db.commit()
    await async_db.refresh(new_product)   # 补上 refresh：原代码漏了这行，不 refresh 返回的 product 没有 id（数据库自增主键还没拿回来）
    return new_product


# 修改商品：仅管理员
@router.patch("/{id}", response_model=ProductResponse)
async def update_product(
        id: int,
        product_update: ProductUpdate,                      # 没有默认值的参数必须排在前面（Python 语法要求）
        current_user: User = Depends(get_current_admin),    # 有默认值的参数排在后面
        async_db: asyncSession = Depends(get_db),
):
    sql=select(Product).where(Product.id==id)
    results = await async_db.execute(sql)
    product = results.scalars().first()
    if product is None:   # 同上，修复 results/product 判空 bug
        raise HTTPException(status_code=404,detail="你要修改的id不存在")
    if product_update.name is not None:
        product.name=product_update.name        #product.name 通常指的是 数据库 ORM 模型对象。 Model里的__tablename__ = "products"
    if product_update.price is not None:
        product.price=product_update.price
    if product_update.stock is not None:
        product.stock=product_update.stock
    if product_update.is_active is not None:
        product.is_active=product_update.is_active
    await async_db.commit()
    await async_db.refresh(product)   # 补 refresh，确保返回最新数据
    return product


# 删除商品：仅管理员
@router.delete("/{id}")
async def delete_product(
        id: int,
        current_user: User = Depends(get_current_admin),   # 仅管理员
        async_db: asyncSession = Depends(get_db),
):
    sql=select(Product).where(Product.id==id)
    results = await async_db.execute(sql)
    product = results.scalars().first()
    if product is None:
        raise HTTPException(status_code=404,detail="你要删除的id不存在")
    await async_db.delete(product)
    await async_db.commit()
    return {"msg":"删除成功"}
