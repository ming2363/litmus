package com.litmus.physics;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * 旋转正多边形内小球碰撞物理模拟器。
 */
public class Simulation {
    private final PolygonConfig config;
    private double x;
    private double y;
    private double vx;
    private double vy;
    private double theta;

    public Simulation(PolygonConfig config, BallState initialState) {
        if (config == null || initialState == null) {
            throw new IllegalArgumentException("配置与初始状态不能为空");
        }
        this.config = config;
        this.x = initialState.getX();
        this.y = initialState.getY();
        this.vx = initialState.getVx();
        this.vy = initialState.getVy();
        this.theta = initialState.getTheta();
    }

    public PolygonConfig getConfig() {
        return config;
    }

    public BallState getState() {
        return new BallState(x, y, vx, vy, theta);
    }

    public List<Vec2> getVertices() {
        int n = config.getSides();
        double r = config.getCircumradius();
        List<Vec2> verts = new ArrayList<>(n);
        for (int k = 0; k < n; k++) {
            double ang = theta + (2.0 * Math.PI * k) / n;
            verts.add(new Vec2(r * Math.cos(ang), r * Math.sin(ang)));
        }
        return Collections.unmodifiableList(verts);
    }

    public double minEdgeClearance() {
        int n = config.getSides();
        double apothem = config.apothem();
        double minClear = Double.POSITIVE_INFINITY;
        for (int k = 0; k < n; k++) {
            double midAng = theta + Math.PI * (2 * k + 1) / n;
            double ux = Math.cos(midAng);
            double uy = Math.sin(midAng);
            double clearance = apothem - (x * ux + y * uy) - config.getBallRadius();
            if (clearance < minClear) {
                minClear = clearance;
            }
        }
        return minClear;
    }

    public boolean isInside() {
        return minEdgeClearance() >= -1e-9;
    }

    public void step(double dt) {
        throw new UnsupportedOperationException("step 尚未实现");
    }
}
