import asyncio
import os
import traceback
from monarchmoney import MonarchMoney

# Replace with your actual Monarch Money email and password.
# It is recommended to use environment variables for security.
EMAIL = os.environ.get("MONARCH_EMAIL")
PASSWORD = os.environ.get("MONARCH_PASSWORD")
TOTP = os.environ.get("MONARCH_TOTP")


async def main():
    # if not EMAIL or not PASSWORD or not TOTP:
    #     print("Please set the MONARCH_EMAIL and MONARCH_PASSWORD and MONARCH_TOTP environment variables.")
    #     return

    if not EMAIL or not PASSWORD:
        print(
            "Please set the MONARCH_EMAIL and MONARCH_PASSWORD environment variables."
        )
        return

    mm = MonarchMoney()
    try:
        try:
            mm.load_session()
            # Immediately test if session is valid
            try:
                await mm.get_subscription_details()
            except Exception as e:
                print(f"An error occurred: {e}")
                traceback.print_exc()
                raise ValueError("Invalid session, need to re-login.")
        except FileNotFoundError:
            os.makedirs(".mm", exist_ok=True)
        except ValueError:
            print("ValueError: Need to re-login...")
            if os.path.exists(".mm/mm_session.pickle"):
                os.remove(".mm/mm_session.pickle")
            del mm._headers["Authorization"]

        print("Attempting to log in...")
        # await mm.multi_factor_authenticate(
        # 	EMAIL,
        # 	PASSWORD,
        # 	TOTP
        # )
        await mm.login(EMAIL, PASSWORD, mfa_secret_key=TOTP)
        print("Login successful! Session retained.")

        print("Obtaining subscription id")
        subs = await mm.get_subscription_details()
        # subscription_id = subs['id']
        print(f"Subscription id: {subs['subscription']['id']}")

        # Try to fetch accounts to verify the session is active
        print("Fetching accounts to test the session...")
        account_data = await mm.get_accounts()

        if account_data:
            accounts = account_data["accounts"]
            print("Successfully fetched accounts!")
            print(f"Found {len(accounts)} accounts.")
            # print(f"{accounts}")
        else:
            print("Successfully logged in, but no accounts were returned.")

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        print(
            "The session may not have been retained. The fix might not be working correctly."
        )


if __name__ == "__main__":
    asyncio.run(main())
