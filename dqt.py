def calculate_10Q7(inflow_tmc):
    # Convert inflow to a 10-day flow (1 TMC = 10^9 cubic meters)
    daily_flow_cubic_meters = (inflow_tmc * 10**9) / (10*300)  # Divide by 10 days
    return daily_flow_cubic_meters / (7 * 24 * 60 * 60)  # Convert to m³/s

# Example inflow value
inflow = 5  # in TMC (example value)

ten_q7 = calculate_10Q7(inflow)
print(f"10Q7 Flow: {ten_q7:.2f} m³/s")