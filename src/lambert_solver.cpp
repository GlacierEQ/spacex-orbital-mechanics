#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>

// Historical filename retained for repository lineage.
// This program is a two-radius Hohmann transfer-speed estimate, NOT a Lambert
// boundary-value solver. It does not solve for a trajectory from r1/r2 vectors
// and time-of-flight and therefore must not be represented as Lambert capability.

constexpr const char* kEvidenceState =
    "LOCAL_ORBITAL_MATH_NOT_FLIGHT_DYNAMICS_AUTHORITY";
constexpr double kMuEarthKm3S2 = 398600.4418;

double hohmann_departure_speed_km_s(double r1_km, double r2_km) {
    if (!(r1_km > 0.0) || !(r2_km > 0.0)) {
        throw std::invalid_argument("orbital radii must be positive");
    }
    const double transfer_a_km = (r1_km + r2_km) / 2.0;
    return std::sqrt(
        kMuEarthKm3S2 * (2.0 / r1_km - 1.0 / transfer_a_km));
}

int main() {
    const double r1_km = 6771.0;
    const double r2_km = 42164.0;
    const double departure_speed = hohmann_departure_speed_km_s(r1_km, r2_km);

    std::cout << kEvidenceState << "\n";
    std::cout << std::fixed << std::setprecision(6)
              << "Hohmann transfer departure speed estimate: "
              << departure_speed << " km/s\n";
    return 0;
}
