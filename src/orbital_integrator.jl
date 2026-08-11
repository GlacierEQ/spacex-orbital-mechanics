# Repository-local two-body Euler-step reference sketch.
#
# This is not an N-body, high-precision, production, or SpaceX trajectory
# integrator. It is intentionally outside the admitted proof surface until a
# Julia runtime gate and numerical-convergence evidence are added.
module OrbitalIntegrator

using LinearAlgebra

const EVIDENCE_STATE = "LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY"
const MU_EARTH_KM3_S2 = 398600.4418

struct OrbitalState
    r::Vector{Float64}
    v::Vector{Float64}
end

function euler_two_body_step(state::OrbitalState, dt::Float64)
    r_mag = norm(state.r)
    r_mag > 0.0 || throw(ArgumentError("position magnitude must be positive"))
    acceleration = -MU_EARTH_KM3_S2 * state.r / (r_mag^3)
    new_v = state.v + acceleration * dt
    new_r = state.r + new_v * dt
    return OrbitalState(new_r, new_v)
end

# Historical alias retained for source compatibility. The method remains a
# first-order Euler step; the name does not imply an exact Kepler propagator.
kepler_step(state::OrbitalState, dt::Float64) = euler_two_body_step(state, dt)

end
