import pandas as pd
import pvlib
from pvlib import solarposition, irradiance

def calculate_daily_energy(latitude, longitude, start_date, end_date, panel_efficiency=0.15):
    # Create a date range for the specified period
    date_range = pd.date_range(start=start_date, end=end_date, freq='D', tz='UTC')

    # Get solar position data
    solar_position = solarposition.get_solarposition(date_range, latitude, longitude)

    # Get extraterrestrial radiation
    dni_extra = irradiance.get_extra_radiation(date_range)

    # Get atmospheric pressure data (optional, but used for a more accurate estimate)
    pressure = pvlib.atmosphere.alt2pres(0)

    # Calculate solar radiation on the inclined plane (surface of the solar panel)
    surface_tilt = 20  # You can adjust this value based on the tilt of your solar panels
    surface_azimuth = 180  # You can adjust this value based on the orientation of your solar panels
    solar_radiation = irradiance.get_total_irradiance(surface_tilt, surface_azimuth,
                                                      solar_position['apparent_zenith'],
                                                      solar_position['azimuth'],
                                                      dni_extra,
                                                      pressure=pressure)

    # Consider panel efficiency and temperature coefficients
    temperature_model = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    temperature_params = pvlib.temperature.sapm_celltemp(solar_radiation['poa_global'],
                                                         solar_position['apparent_zenith'],
                                                         solar_position['apparent_azimuth'],
                                                         temperature_model)

    # Calculate DC power using the SAPM model
    system = {'surface_tilt': surface_tilt, 'surface_azimuth': surface_azimuth,
              'module_parameters': {'pdc0': 240, 'gamma_pdc': -0.004}}
    dc_power = pvlib.pvsystem.sapm(solar_radiation['poa_global'], temperature_params['temp_cell'],
                                   system['module_parameters'])

    # Calculate daily energy in kWh
    daily_energy = dc_power.sum() * panel_efficiency / 1000  # convert from W to kW

    return daily_energy

# Example usage
latitude = 37.7749  # Example latitude for San Francisco, CA
longitude = -122.4194  # Example longitude for San Francisco, CA
start_date = '2023-01-01'
end_date = '2023-01-10'

result = calculate_daily_energy(latitude, longitude, start_date, end_date)
print(f"Estimated daily energy generation: {result:.2f} kWh")

