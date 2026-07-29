# Julia Differential Orbital Integrator for SpaceX Trajectories
module OrbitalIntegrator

using LinearAlgebra

struct OrbitalState
    r::Vector{Float64}
    v::Vector{Float64}
end

function kepler_step(state::OrbitalState, dt::Float64)
    μ = 398600.4418
    r_mag = norm(state.r)
    a = -μ * state.r / (r_mag^3)
    new_v = state.v + a * dt
    new_r = state.r + new_v * dt
    return OrbitalState(new_r, new_v)
end

end
