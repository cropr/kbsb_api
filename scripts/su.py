import asyncio
from fastapi import FastAPI
from reddevil.core import (
    register_app,
    connect_mongodb,
    close_mongodb,
)

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")

from reddevil.account import (
    add_account,
    AccountInValidator,
    LoginType,
    update_password,
    AccountPasswordUpdateValidator,
)


async def main():
    """
    create a superaccount
    """
    await connect_mongodb()

    # create account
    await add_account(
        AccountInValidator(
            email="",
            enabled=True,
            first_name="",
            id="eddy",
            last_name="",
            locale="",
            logintype=LoginType.email,
            password="",
        )
    )
    await update_password(
        AccountPasswordUpdateValidator(
            username="eddy", newpassword="kannibaal", oldpassword=""
        ),
        checkold=False,
    )
    await close_mongodb()


if __name__ == "__main__":
    asyncio.run(main())
