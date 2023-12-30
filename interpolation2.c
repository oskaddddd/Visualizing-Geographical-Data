#define DistI(PointLayer, section) ((r[1]*r[2]*2*PointLayer)+i+section)

kernel void CalculateDistances(
    //rmpp, ry, rx, rp
    global ushort  *r,
    global short *points, 
    global float *out) {

    int y = get_global_id(0);
    int x = get_global_id(1);
    
    int i = (r[2] * y*2) + (x*2);
    //indexing
    out[i] = y;
    out[DistI(2, 0)] = x;
    out[DistI(1, 1)] = 69;


}