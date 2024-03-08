from utils import jsonify
from fastapi import APIRouter, HTTPException
from database.models import Org, User
from database.connection import db
from sqlalchemy import select, func, update, delete
from api.version import API_PREFIX
router = APIRouter(
    prefix= API_PREFIX + '/orgs',
    tags = ['orgs']
)

@router.get('/')
async def get_orgs(filter: str = '', case: bool = False):
    async with db.create_session_readonly() as s:
        if case:  # case sensitive
            result = await s.execute(select(Org.name, Org.createTime).filter(Org.name.like(f'%{filter}%')))
        else:
            result = await s.execute(select(Org.name, Org.createTime).filter(func.lower(Org.name).like(func.lower(f'%{filter}%'))))
        return jsonify(result.all())

@router.get('/{name}')
async def get_org(name: str):
    async with db.create_session_readonly() as s:
        result = await s.execute(select(Org.name, Org.createTime).filter(Org.name == name))
        return jsonify(result.one_or_none())

@router.get('/{org_name}/usercount')
async def get_org_user_count(org_name: str):
    async with db.create_session_readonly() as s:
        return await s.scalar(select(func.count()).select_from(select(User).filter(User.org == org_name).subquery()))

@router.post('/{name}')
async def create_org(name: str):
    async with db.create_session() as s:
        async with s.begin():
            if (await s.execute(select(Org).filter(Org.name == name))).one_or_none():
                raise HTTPException(400, f"{Org.__name__} {name} already exists")
            s.add(Org(name=name))

@router.patch('/{name}/{newname}')
async def rename_org(name: str, newname: str):
    async with db.create_session() as s:
        async with s.begin():
            if (await s.execute(select(Org).filter(Org.name == name))).one_or_none() is None:
                raise HTTPException(400, f"{Org.__name__} {name} does not exist")
            if (await s.execute(select(Org).filter(Org.name == newname))).one_or_none():
                raise HTTPException(400, f"{Org.__name__} {newname} exists")
            await s.execute(update(Org).where(Org.name==name).values(name=newname))

@router.delete('/{name}')
async def delete_org(name: str):
    async with db.create_session() as s:
        async with s.begin():
            if (await s.execute(select(Org).filter(Org.name == name))).one_or_none() is None:
                raise HTTPException(400, f"{Org.__name__} {name} does not exist")
            if user_count := await get_org_user_count(name) > 0:
                raise HTTPException(400, f"Cannot delete {Org.__name__} {name} because it has {user_count} users. Delete all of its users first.")
            await s.execute(delete(Org).where(Org.name==name))
