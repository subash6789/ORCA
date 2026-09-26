import asyncio
from datetime import datetime

from load_ocean_to_db import load_ocean_data


async def automatic_update_loop():

    while True:

        print(
            f"[ORCA AUTO UPDATE] "
            f"Starting real data update: {datetime.now()}"
        )

        try:
            load_ocean_data()

            print(
                "[ORCA AUTO UPDATE] "
                "Real ocean data update completed successfully."
            )

        except Exception as error:
            print(
                "[ORCA AUTO UPDATE] "
                f"Update failed: {error}"
            )

        await asyncio.sleep(3600)