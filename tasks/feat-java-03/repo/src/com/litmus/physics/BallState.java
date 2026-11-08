package com.litmus.physics;

/**
 * 小球与多边形旋转角的不可变状态快照。
 */
public final class BallState {
    private final double x;
    private final double y;
    private final double vx;
    private final double vy;
    private final double theta;

    public BallState(double x, double y, double vx, double vy, double theta) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.theta = theta;
    }

    public double getX() {
        return x;
    }

    public double getY() {
        return y;
    }

    public double getVx() {
        return vx;
    }

    public double getVy() {
        return vy;
    }

    public double getTheta() {
        return theta;
    }

    public double kineticEnergyPerUnitMass() {
        return 0.5 * (vx * vx + vy * vy);
    }
}
