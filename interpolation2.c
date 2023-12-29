kernel void CalculateDistances(global int *r, global int *points, global int *out) {
    int p = get_global_id(0);
    int y = get_global_id(1);
    int x = get_global_id(2);
    //rp, ry, rx
    int i = (r[2] * r[1] * p) + (r[2] * y) + x;

    out[i] = r[1];


}