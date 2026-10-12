import asyncio
from datetime import datetime

from incois_hycom_collector import (
    collect_hycom,
    save_hycom_data
)

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
        # OCEAN / HYCOM
        # -------------------------------------------------

        try:

            print()
            print("[1/5] Updating INCOIS HYCOM ocean data...")

            ocean_results = await asyncio.to_thread(
                collect_hycom
            )

            if ocean_results:
                save_stats = await asyncio.to_thread(
                    save_hycom_data,
                    ocean_results
                )
                stats_str = ""
                if isinstance(save_stats, dict):
                    stats_str = (
                        f" (inserted={save_stats.get('inserted', 0)}, "
                        f"updated={save_stats.get('updated', 0)}, "
                        f"skipped={save_stats.get('skipped', 0)})"
                    )
                print(
                    f"HYCOM ocean update completed: "
                    f"{len(ocean_results)} collected records{stats_str}."
                )
            else:
                print(
                    "HYCOM ocean update warning: No regional records collected."
                )

        except Exception as error:

            print(
                f"HYCOM ocean update FAILED: {error}"
            )

        # -------------------------------------------------
        # CHLOROPHYLL
        # -------------------------------------------------

        try:

            print()
            print("[2/5] Updating chlorophyll...")

            await asyncio.to_thread(
                create_chlorophyll_table
            )

            chl_results = await asyncio.to_thread(
                collect_chlorophyll_data
            )

            if chl_results:
                await asyncio.to_thread(
                    save_chlorophyll_data,
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

            await asyncio.to_thread(
                create_wind_forecast_table
            )

            wind_results = await asyncio.to_thread(
                collect_wind_data
            )

            if wind_results:
                await asyncio.to_thread(
                    save_wind_data,
                    wind_results
                )

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

            await asyncio.to_thread(
                create_pfz_table
            )

            pfz_results = await asyncio.to_thread(
                collect_pfz
            )

            print(
                f"PFZ update completed: "
                f"{len(pfz_results) if pfz_results else 0} rows."
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

            await asyncio.to_thread(
                create_satellite_table
            )

            satellite_results = await asyncio.to_thread(
                collect_satellite_data
            )

            if satellite_results:
                await asyncio.to_thread(
                    save_satellite_data,
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