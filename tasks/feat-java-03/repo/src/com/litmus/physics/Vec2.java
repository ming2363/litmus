package com.litmus.physics;

/**
 * 二维不可变向量值对象。
 */
public final class Vec2 {
    public final double x;
    public final double y;

    public Vec2(double x, double y) {
        this.x = x;
        this.y = y;
    }

    public Vec2 add(Vec2 other) {
        return new Vec2(this.x + other.x, this.y + other.y);
    }

    public Vec2 sub(Vec2 other) {
        return new Vec2(this.x - other.x, this.y - other.y);
    }

    public Vec2 scale(double factor) {
        return new Vec2(this.x * factor, this.y * factor);
    }

    public double dot(Vec2 other) {
        return this.x * other.x + this.y * other.y;
    }

    public double length() {
        return Math.hypot(x, y);
    }
}
