from databases import Database

from .models import user, password


async def get_users(db: Database):
    query = user.select()
    return await db.fetch_all(query=query)


async def create_user(data, db: Database):
    password_string = data.pop('password')
    insert_password_query = password.insert().values(password=password_string)
    new_password_id = await db.execute(query=insert_password_query)

    query = user.insert().values(**data, password_id=new_password_id)
    return await db.execute(query=query)


async def get_user_by_id(id: int, db: Database):
    query = user.select().where(user.c.id == id)
    return await db.fetch_one(query=query)


async def delete_user(id: int, db: Database):
    query = user.delete().where(user.c.id == id)
    return await db.execute(query=query)

