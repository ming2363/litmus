package com.litmus.physics;

/**
 * 旋转正多边形容器与物理模拟参数配置。
 */
public final class PolygonConfig {
    private final int sides;
    private final double circumradius;
    private final double omega;
    private final double gravity;
    private final double restitution;
    private final double ballRadius;

    public PolygonConfig(
            int sides,
            double circumradius,
            double omega,
            double gravity,
            double restitution,
            double ballRadius) {
        if (sides < 3) {
            throw new IllegalArgumentException("多边形边数必须 >= 3: " + sides);
        }
        if (!Double.isFinite(circumradius) || circumradius <= 0.0) {
            throw new IllegalArgumentException("外接圆半径必须为有限正数: " + circumradius);
        }
        if (!Double.isFinite(omega)) {
            throw new IllegalArgumentException("角速度必须为有限数值: " + omega);
        }
        if (!Double.isFinite(gravity) || gravity < 0.0) {
            throw new IllegalArgumentException("重力加速度必须为有限非负数: " + gravity);
        }
        if (!Double.isFinite(restitution) || restitution < 0.0 || restitution > 1.0) {
            throw new IllegalArgumentException("恢复系数必须在 [0, 1] 内: " + restitution);
        }
        double apothem = circumradius * Math.cos(Math.PI / sides);
        if (!Double.isFinite(ballRadius) || ballRadius < 0.0 || ballRadius >= apothem * 0.95) {
            throw new IllegalArgumentException("小球半径非法或过大: " + ballRadius);
        }
        this.sides = sides;
        this.circumradius = circumradius;
        this.omega = omega;
        this.gravity = gravity;
        this.restitution = restitution;
        this.ballRadius = ballRadius;
    }

    public int getSides() {
        return sides;
    }

    public double getCircumradius() {
        return circumradius;
    }

    public double getOmega() {
        return omega;
    }

    public double getGravity() {
        return gravity;
    }

    public double getRestitution() {
        return restitution;
    }

    public double getBallRadius() {
        return ballRadius;
    }

    public double apothem() {
        return circumradius * Math.cos(Math.PI / sides);
    }
}
