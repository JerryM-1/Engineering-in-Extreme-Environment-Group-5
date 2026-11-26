"""MOC solver copied unchanged from MECH0074_Stage1_LNG.ipynb (supplied teaching solver)."""
import numpy as np
g = 9.81
def simulate_water_hammer(
    length=600.0,
    diameter=0.30,
    wave_speed=1000.0,
    friction_factor=0.020,
    initial_velocity=1.0,
    reservoir_head=120.0,
    closure_time=0.01,
    density=998.0,
    n_reaches=80,
    n_round_trips=4.0,
    simulation_time=None,
):
    """MOC solution for a reservoir-pipe-valve system.

    Head is gauge piezometric head relative to the pipe elevation. The valve
    boundary has a prescribed linear reduction of volume flow to zero.
    """
    values = [length, diameter, wave_speed, initial_velocity, density, n_reaches]
    if min(values) <= 0 or closure_time <= 0 or friction_factor < 0:
        raise ValueError("Physical dimensions, speed, density and closure time must be positive.")

    n_reaches = int(n_reaches)
    area = np.pi * diameter**2 / 4
    dx = length / n_reaches
    dt = dx / wave_speed                      # exact rectangular characteristic grid
    round_trip = 2 * length / wave_speed
    end_time = (closure_time + n_round_trips * round_trip
                if simulation_time is None else float(simulation_time))
    if end_time <= 0:
        raise ValueError("Simulation time must be positive.")
    n_steps = int(np.ceil(end_time / dt))

    x = np.linspace(0.0, length, n_reaches + 1)
    time = np.arange(n_steps + 1) * dt
    H = np.empty((n_steps + 1, n_reaches + 1), dtype=float)
    Q = np.empty_like(H)

    Q_initial = area * initial_velocity
    # Horizontal steady-state head profile with Darcy-Weisbach loss.
    H_initial = reservoir_head - friction_factor * x * initial_velocity**2 / (2 * g * diameter)
    H[0] = H_initial
    Q[0] = Q_initial

    B = wave_speed / (g * area)
    R = friction_factor * dx / (2 * g * diameter * area**2)

    for n in range(n_steps):
        h_old, q_old = H[n], Q[n]

        # Interior nodes: one compatibility relation arrives from each side.
        c_plus = h_old[:-2] + B*q_old[:-2] - R*q_old[:-2]*np.abs(q_old[:-2])
        c_minus = h_old[2:] - B*q_old[2:] + R*q_old[2:]*np.abs(q_old[2:])
        H[n+1, 1:-1] = 0.5 * (c_plus + c_minus)
        Q[n+1, 1:-1] = (c_plus - c_minus) / (2 * B)

        # Upstream reservoir: fixed head; incoming C- comes from node 1.
        c_minus_res = h_old[1] - B*q_old[1] + R*q_old[1]*abs(q_old[1])
        H[n+1, 0] = reservoir_head
        Q[n+1, 0] = (H[n+1, 0] - c_minus_res) / B

        # Downstream valve: prescribed linear flow closure.
        c_plus_valve = h_old[-2] + B*q_old[-2] - R*q_old[-2]*abs(q_old[-2])
        opening = max(1.0 - time[n+1] / closure_time, 0.0)
        Q[n+1, -1] = Q_initial * opening
        H[n+1, -1] = c_plus_valve - B * Q[n+1, -1]

    return {
        "x": x,
        "time": time,
        "H": H,
        "Q": Q,
        "H_initial": H_initial,
        "area": area,
        "dx": dx,
        "dt": dt,
        "B": B,
        "R": R,
        "round_trip": round_trip,
        "density": density,
        "diameter": diameter,
        "wave_speed": wave_speed,
        "initial_velocity": initial_velocity,
        "closure_time": closure_time,
        "reservoir_head": reservoir_head,
        "friction_factor": friction_factor,
        "Q_initial": Q_initial,
    }