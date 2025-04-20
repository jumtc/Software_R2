import random
import time
import json
from datetime import datetime

battery = 100.0
x_position = 0.0
y_position = 1.0  # strictly positive to start
distance = 0.0
iteration = 1

total_iterations = 12000
battery_drain_per_iter = 100.0 / total_iterations
time_per_iter = 0.01
gyroscope_range = (-0.15, 0.15)

state = "IDLE"  # Drone state

start_time = datetime.now()

def get_sensor_status(battery, altitude):
    if battery < 10:
        return "RED"
    if altitude < 3:
        return "RED"
    elif altitude < 1000:
        return "YELLOW"
    else:
        return "GREEN"

with open('telemetry_log.json', 'w') as log_file:
    print(f"{start_time.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} [INFO] Initializing drone simulator with telemetry file: telemetry_log.json", file=log_file)

    while battery > 0 and iteration <= total_iterations:
        current_time = datetime.now()
        timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

        speed = round(random.uniform(0, 5), 2)
        altitude = round(random.uniform(1.5, 1050), 2)  # allow for GREEN signal possibility

        if state == "IDLE":
            input_command = {'speed': 0, 'altitude': altitude, 'movement': 'none'}
            state = "TAKEOFF"

        elif state == "TAKEOFF":
            y_position += 1
            y_position = max(y_position, 0.01)
            input_command = {'speed': 0, 'altitude': y_position, 'movement': 'ascend'}
            if y_position >= 5:
                state = "FLYING"

        elif state == "FLYING":
            x_position += speed
            y_position += max(0.01, random.uniform(0.01, 0.5))
            distance += speed
            input_command = {'speed': speed, 'altitude': altitude, 'movement': 'fwd'}
            if battery < 10:
                state = "LANDING"

        elif state == "LANDING":
            y_position = max(0.01, y_position - 0.5)
            altitude = y_position
            input_command = {'speed': 0, 'altitude': altitude, 'movement': 'descend'}
            if y_position <= 1.0:
                state = "CRASHED"
                break

        telemetry = {
            "iteration": iteration,
            "timestamp": timestamp,
            "x_position": round(x_position, 2),
            "y_position": round(y_position, 2),
            "altitude": altitude,
            "battery": round(battery, 2),
            "gyroscope": [round(random.uniform(*gyroscope_range), 12) for _ in range(3)],
            "wind_speed": round(random.uniform(0, 5), 10),
            "dust_level": round(random.uniform(0, 2), 10),
            "sensor_status": get_sensor_status(battery, altitude)
        }

        json.dump(telemetry, log_file, indent=3)
        log_file.write("\n")

        battery -= battery_drain_per_iter
        iteration += 1
        time.sleep(time_per_iter)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    final_status = "Battery zero, drone crashed"

    # Calculating the actual time duration and converting to minutes
    total_seconds = round(duration)
    total_minutes = total_seconds // 60  # Convert to minutes
    remaining_seconds = total_seconds % 60  # Remaining seconds after minutes calculation

    log_file.write(f"\nFinal status: {final_status}\n")
    log_file.write(f"Total distance: {round(distance, 2)} units\n")
    log_file.write(f"{total_iterations} iterations = {total_minutes} min {remaining_seconds} sec\n")
    log_file.write(f"{final_status}\n")

print("Simulation complete. Telemetry data saved to 'telemetry_log.json'.")
