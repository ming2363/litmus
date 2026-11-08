package com.litmus.physics;

import java.util.List;

public class SimulationPublicTest {

    private static void assertTrue(boolean cond, String msg) {
        if (!cond) {
            throw new AssertionError(msg);
        }
    }

    public void testPolygonGeometryAndConfigValidation() {
        PolygonConfig cfg = new PolygonConfig(4, 10.0, 0.0, 9.8, 1.0, 0.5);
        Simulation sim = new Simulation(cfg, new BallState(0.0, 0.0, 0.0, 0.0, Math.PI / 4.0));
        assertTrue(sim.isInside(), "中心点应在多边形内");
        double expectedApothem = 10.0 * Math.cos(Math.PI / 4.0);
        double clearance = sim.minEdgeClearance();
        assertTrue(Math.abs(clearance - (expectedApothem - 0.5)) < 1e-6, "内切余量计算误差过大");

        List<Vec2> verts = sim.getVertices();
        assertTrue(verts.size() == 4, "四边形应有 4 个顶点");

        boolean threw = false;
        try {
            new PolygonConfig(2, 10.0, 0.0, 9.8, 1.0, 0.1);
        } catch (IllegalArgumentException expected) {
            threw = true;
        }
        assertTrue(threw, "边数小于 3 应抛异常");
    }
}
