from aiohttp import web
import json
from db import Ad, engine, Session, Base
from sqlalchemy.exc import IntegrityError, DBAPIError
from typing import Type
from pydantic import BaseModel, ValidationError

class AdValidate(BaseModel):
    id: int
    title: str
    description: str
    # creation_time = Column(DateTime, server_default=func.now(), unique=False)
    owner: str


app = web.Application()

async def orm_context(app_: web.Application):
    print("Start")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("SHUTDOWN")



ERROR_TYPE = Type[web.HTTPConflict]

def raise_http_error(error_class: ERROR_TYPE, message: str | dict):
    raise error_class(
        text=json.dumps({"status": "error", "description": message}),
        content_type="application/json",
    )


@web.middleware
async def session_middleware(requests: web.Request, handler):
    async with Session() as session:
        requests["session"] = session
        return await handler(requests)

app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)
# app.middlewares.append(error_middleware)
# app = web.Application(middlewares=[session_middleware, error_middleware])


async def get_ad(ad_id: int, session: Session):
    ad = await session.get(Ad, ad_id)
    if ad is None:
        raise web.HTTPNotFound(
            text=json.dumps({"status": "error", "message": "ad not found"}),
            content_type="application/json",
        )
    return ad


class Advertisement(web.View):
    async def get(self):
        ad_id = int(self.request.match_info["ad_id"])
        ad = await get_ad(ad_id, self.request["session"])
        return web.json_response(
            {
                "id": ad.id,
                "title": ad.title,
                "description": ad.description,
                "creation_time": ad.creation_time.isoformat(),
                "owner": ad.owner,
            }
        )

    async def post(self):
        session = self.request["session"]
        json_data = await self.request.json()
        ad = Ad(**json_data)
        session.add(ad)
        try:
            await session.commit()
        except IntegrityError:
            raise web.HTTPConflict(
                text=json.dumps({"status": "error", "message": "user already exists"}),
                content_type="application/json",
            )

        return web.json_response({"id": ad.id})

    async def patch(self):
        ad_id = int(self.request.match_info["ad_id"])
        ad = await get_ad(ad_id, self.request["session"])
        json_data = await self.request.json()
        for field, value in json_data.items():
            setattr(ad, field, value)
        self.request["session"].add(ad)
        await self.request["session"].commit()
        return web.json_response({"status": "success"})

    async def delete(self):
        ad_id = int(self.request.match_info["ad_id"])
        ad = await get_ad(ad_id, self.request["session"])
        await self.request["session"].delete(ad)
        await self.request["session"].commit()
        return web.json_response({"status": "success"})


app.add_routes(
    [
        web.get(r"/ads/{ad_id:\d+}/", Advertisement),
        web.post(r"/ads/", Advertisement),
        web.patch(r"/ads/{ad_id:\d+}/", Advertisement),
        web.delete(r"/ads/{ad_id:\d+}/", Advertisement),
    ]
)

if __name__ == "__main__":
    web.run_app(app, port=111)
