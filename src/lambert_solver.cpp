#include <iostream>
#include <cmath>

struct Vector3D {
    double x, y, z;
    double magnitude() const {
        return std::sqrt(x*x + y*y + z*z);
    }
};

class LambertSolver {
public:
    double compute_delta_v(const Vector3D& r1, const Vector3D& r2, double tof_seconds) {
        double mu = 398600.4418; // Earth gravitational parameter km^3/s^2
        double r1_mag = r1.magnitude();
        double r2_mag = r2.magnitude();
        double semi_major_axis = (r1_mag + r2_mag) / 2.0;
        double v_transfer = std::sqrt(mu * (2.0 / r1_mag - 1.0 / semi_major_axis));
        return v_transfer;
    }
};

int main() {
    LambertSolver solver;
    Vector3D r1{6771.0, 0.0, 0.0};
    Vector3D r2{0.0, 42164.0, 0.0};
    double dv = solver.compute_delta_v(r1, r2, 18000.0);
    std::cout << "Lambert Transfer Delta-V: " << dv << " km/s" << std::endl;
    return 0;
}
