import asyncio
from datetime import datetime

from load_ocean_to_db import load_ocean_data

from incois_chl_collector import (
    create_chlorophyll_table,
    collect_chlorophyll_data,
    save_chlorophyll_data,
)

from incois_wind_collector import (
    create_wind_forecast_table,
    collect_wind_data,
)

from pfz_collector import (
    create_pfz_table,
    collect_pfz,
)

from satellite_collector import (
    create_satellite_table,
    collect_satellite_data,
    save_satellite_data,
)


async def automatic_update_loop():

    while True:

        print()
        print("=" * 70)
        print(
            "ORCA AUTOMATIC REAL-DATA UPDATE "
            f"{datetime.now().isoformat()}"
        )
        print("=" * 70)

        # =================================================
        # 1. OCEAN
        # =================================================

        try:

            print()
            print("[1/5] Updating ocean observations...")

            load_ocean_data()

            print(
                "Ocean update completed successfully."
            )

        except Exception as error:

            print(
                f"Ocean update FAILED: {error}"
            )

        # =================================================
        # 2. CHLOROPHYLL
        # =================================================

        try:

            print()
            print("[2/5] Updating chlorophyll...")

            create_chlorophyll_table()

            chl_results = (
                collect_chlorophyll_data()
            )

            if chl_results:

                save_chlorophyll_data(
                    chl_results
                )

            print(
                "Chlorophyll update completed: "
                f"{len(chl_results)} records."
            )

        except Exception as error:

            print(
                f"Chlorophyll update FAILED: {error}"
            )

        # =================================================
        # 3. WIND + WAVE
        # =================================================

        try:

            print()
            print(
                "[3/5] Updating INCOIS wind/wave..."
            )

            create_wind_forecast_table()

            wind_results = (
                collect_wind_data()
            )

            print(
                "Wind/Wave update completed: "
                f"{len(wind_results)} regional records."
            )

        except Exception as error:

            print(
                f"Wind/Wave update FAILED: {error}"
            )

        # =================================================
        # 4. PFZ
        # =================================================

        try:

            print()
            print(
                "[4/5] Updating INCOIS PFZ..."
            )

            create_pfz_table()

            pfz_results = collect_pfz()

            print(
                "PFZ update completed: "
                f"{len(pfz_results)} rows."
            )

        except Exception as error:

            print(
                f"PFZ update FAILED: {error}"
            )

        # =================================================
        # 5. SATELLITE
        # =================================================

        try:

            print()
            print(
                "[5/5] Updating EOS-06 satellite data..."
            )

            create_satellite_table()

            satellite_results = (
                collect_satellite_data()
            )

            if satellite_results:

                save_satellite_data(
                    satellite_results
                )

            print(
                "Satellite update completed: "
                f"{len(satellite_results)} records."
            )

        except Exception as error:

            print(
                f"Satellite update FAILED: {error}"
            )

        # =================================================
        # CYCLE COMPLETE
        # =================================================

        print()
        print("=" * 70)
        print(
            "ORCA REAL-DATA UPDATE CYCLE COMPLETED"
        )
        print(
            "Waiting 1 hour for the next automatic update..."
        )
        print("=" * 70)

        await asyncio.sleep(3600)


if __name__ == "__main__":

    asyncio.run(
        automatic_update_loop()
    )