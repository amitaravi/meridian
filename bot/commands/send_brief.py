"""
Manual brief trigger for testing.

Usage (from the bot/ directory):
    python -m commands.send_brief --user_id=<UUID>

Requires .env to be populated with TELEGRAM_BOT_TOKEN, SUPABASE_URL,
SUPABASE_SERVICE_ROLE_KEY, and GROQ_API_KEY.
"""
import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()


async def _run(user_id: str) -> None:
    from telegram import Bot

    from app.db.users import get_user_by_id
    from app.services.brief import send_brief

    user = get_user_by_id(user_id)
    if not user:
        print(f"Error: no user found with id={user_id}", file=sys.stderr)
        sys.exit(1)

    bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    async with bot:
        await send_brief(user_id, user["telegram_id"], bot)

    print(f"Brief sent to telegram_id={user['telegram_id']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a daily brief to one user")
    parser.add_argument("--user_id", required=True, help="Internal UUID from the users table")
    args = parser.parse_args()
    asyncio.run(_run(args.user_id))
