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


async def handle_request(request):
    try:
        # Parse the JSON data from the request using the Person model
        data = await request.json()
        person = AdValidate(**data)
    except ValidationError:
        raise web.HTTPConflict(
            text=json.dumps({"status": "error", "message": "content type error"}),
            content_type="application/json",
        )


@web.middleware
async def session_middleware(requests: web.Request, handler):
    async with Session() as session:
        requests["session"] = session
        return await handler(requests)


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


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
        a = await handle_request(self.request)
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
