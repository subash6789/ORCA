import asyncio
from datetime import datetime

from load_ocean_to_db import load_ocean_data

from incois_chl_collector import (
    create_chlorophyll_table,
    collect_chlorophyll_data,
    save_chlorophyll_data
)

from incois_wind_collector import (
    create_wind_forecast_table,
    collect_wind_data,
    save_wind_data
)

from pfz_collector import (
    create_pfz_table,
    collect_pfz
)

from satellite_collector import (
    create_satellite_table,
    collect_satellite_data,
    save_satellite_data
)


async def automatic_update_loop():

    while True:

        print()
        print("=" * 70)
        print(
            f"ORCA AUTOMATIC REAL-DATA UPDATE "
            f"{datetime.now().isoformat()}"
        )
        print("=" * 70)

        # -------------------------------------------------
        # OCEAN
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CHLOROPHYLL
        # -------------------------------------------------

        try:

            print()
            print("[2/5] Updating chlorophyll...")

            create_chlorophyll_table()

            chl_results = collect_chlorophyll_data()

            save_chlorophyll_data(
                chl_results
            )

            print(
                "Chlorophyll update completed."
            )

        except Exception as error:

            print(
                f"Chlorophyll update FAILED: {error}"
            )

        # -------------------------------------------------
        # WIND + WAVE
        # -------------------------------------------------

        try:

            print()
            print("[3/5] Updating INCOIS wind/wave...")

            create_wind_forecast_table()

            wind_results = collect_wind_data()

            if wind_results:
                save_wind_data(wind_results)

            print(
                "Wind/Wave update completed."
            )

        except Exception as error:

            print(
                f"Wind/Wave update FAILED: {error}"
            )

        # -------------------------------------------------
        # PFZ
        # -------------------------------------------------

        try:

            print()
            print("[4/5] Updating INCOIS PFZ...")

            create_pfz_table()

            pfz_results = collect_pfz()

            print(
                f"PFZ update completed: "
                f"{len(pfz_results)} rows."
            )

        except Exception as error:

            print(
                f"PFZ update FAILED: {error}"
            )

        # -------------------------------------------------
        # SATELLITE
        # -------------------------------------------------

        try:

            print()
            print("[5/5] Updating EOS-06 satellite data...")

            create_satellite_table()

            satellite_results = collect_satellite_data()

            save_satellite_data(
                satellite_results
            )

            print(
                "Satellite update completed."
            )

        except Exception as error:

            print(
                f"Satellite update FAILED: {error}"
            )

        # -------------------------------------------------
        # WAIT
        # -------------------------------------------------

        print()
        print("=" * 70)
        print(
            "ORCA real-data update cycle completed."
        )
        print(
            "Waiting 1 hour for the next automatic update..."
        )
        print("=" * 70)

        await asyncio.sleep(3600)