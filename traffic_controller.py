import numpy as np

# --- 1. Data Setup ---
daily_density = np.random.randint(10, 100, (1000, 4)).astype(np.int16)
roads = np.array(['Road_A', 'Road_B', 'Road_C', 'Road_D'])
YELLOW_TIME = 10.0
ALL_RED_TIME = 15.0
is_emargency = np.random.choice([True, False], size=4, p=[0.1, 0.9])

# --- 2. Data Cleaning ---
daily_density = np.nan_to_num(daily_density, nan=0)
daily_density = np.clip(daily_density, 0, 100)

# --- 3. Analytics ---
avg_traffic = np.mean(daily_density, axis=0)
extreme_moments = daily_density[daily_density > 85]

# --- 4. Logic Functions ---
def get_priority_index(density, emergency_status):
    priority_score = density.astype(float)
    priority_score[emergency_status] = 999.0
    return np.argsort(priority_score)[::-1]

def calculate_green_times(density, total_traffic, threshold):
    if total_traffic == 0:
        return np.array([30.0, 30.0, 30.0, 30.0])
    return np.where(density >= threshold, 120.0, (density / threshold) * 120.0)

# --- 5. Main Execution ---
def run_traffic_controller():
    try:
        print(f"daily_density : {daily_density}")
        print(f"avg traffic of full day: {np.round(avg_traffic, 1)}")
        print(f"Extreme top 10 traffic moment: {extreme_moments[:10]}")

        traffic_density = daily_density[-1]
        total_traffic = np.sum(traffic_density)

        threshold = np.mean(traffic_density) * 1.1
        load_limit = np.mean(traffic_density) * 0.2

        green_times = calculate_green_times(traffic_density, total_traffic, threshold)
        is_switched = traffic_density < load_limit
        priority_idx = get_priority_index(traffic_density, is_emargency)

        for i in priority_idx:
            if is_emargency[i]:
                print(f"!!! EMERGENCY ON {roads[i]} !!!")

            mask = np.ones(len(roads), dtype=bool)
            mask[i] = False
            print(f"Road: {roads[i]} | Traffic: {traffic_density[i]}")

            if is_switched[i] and not is_emargency[i]:
                print("Green: Switch due to low traffic")
            else:
                print(f"Green: {green_times[i]:.1f}s")

            print(f"Red: {', '.join(roads[mask])}")
            print(f"Yellow: {YELLOW_TIME} | All Red: {ALL_RED_TIME}")
            print('...................')
    except Exception as e:
        print(f'An error occured in traffic controller:{e}')    

if __name__ == "__main__":
    run_traffic_controller()
