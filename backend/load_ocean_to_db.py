import os
import xarray as xr
from db_connection import get_connection

DATA_FOLDER = r"C:\Users\Acer\ORCA\data\ocean_data"
FILE_PATH = os.path.join(DATA_FOLDER, "latest_ocean.nc")


def load_ocean_data():
    print("Opening real ocean data...")

    ds = xr.open_dataset(FILE_PATH)

    sst = float(ds["TEMP"].mean())
    ssh = float(ds["SSH"].mean())
    salinity = float(ds["SALN"].mean())

    u = ds["UVEL"]
    v = ds["VVEL"]
    current_speed = float(((u ** 2 + v ** 2) ** 0.5).mean())

    mld = float(ds["MLD"].mean())

    data_time = str(ds["TIME"].values[0])[:19]
    region = "Tamil Nadu / Bay of Bengal"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO ocean_observation
        (data_time, region, sst_c, ssh_m, salinity,
         current_speed_ms, mld_m)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data_time,
            region,
            sst,
            ssh,
            salinity,
            current_speed,
            mld
        )
    )

    conn.commit()

    cursor.close()
    conn.close()
    ds.close()

    print("Real ocean data inserted into PostgreSQL successfully!")
    print("Time:", data_time)
    print("SST:", round(sst, 2), "°C")
    print("SSH:", round(ssh, 3), "m")
    print("Salinity:", round(salinity, 2))
    print("Current Speed:", round(current_speed, 3), "m/s")
    print("MLD:", round(mld, 2), "m")


if __name__ == "__main__":
    load_ocean_data()