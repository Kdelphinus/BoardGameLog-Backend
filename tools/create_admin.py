import asyncio
import os
import sys

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 명시적 선언
from app.models.user import User
from app.config import settings
from app.api.dependencies import get_db
from app.crud.user import get_user_in_db
from app.core.security import pwd_context


async def create_admin():
    async for db in get_db():  # 스크립트에선 의존성 동작 안 함
        admin = await get_user_in_db(db=db, name="admin")

        if not admin:
            admin = User(
                name="admin",
                email=settings.ADMIN_MAIL,
                password=pwd_context.hash(settings.ADMIN_PWD),
                is_admin=True,  # 관리자 권한 설정
            )
            db.add(admin)
            await db.commit()
            print("✅ Admin 계정이 생성되었습니다.")
        else:
            print("⚠️ Admin 계정이 이미 존재합니다.")

        await db.close()


if __name__ == "__main__":
    asyncio.run(create_admin())
