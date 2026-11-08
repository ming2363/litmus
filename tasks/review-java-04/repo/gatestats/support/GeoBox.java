package gatestats.support;

/** 包围盒与近似距离。坐标是毫度。 */
public final class GeoBox {
    private GeoBox() {
    }

    public static boolean inside(int lat, int lon, int south, int west, int north, int east) {
        if (west > east || south > north) {
            throw new IllegalArgumentException("box");
        }
        return lat >= south && lat <= north && lon >= west && lon <= east;
    }

    public static long distance2(int lat1, int lon1, int lat2, int lon2) {
        long dlat = (long) lat1 - lat2;
        long dlon = (long) lon1 - lon2;
        return dlat * dlat + dlon * dlon;
    }
}
