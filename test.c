kernel void Bilinear(global int *triangles, global int *out, global int *data, global int *Image) {
    
    int g1 = get_global_id(1);
    int g0 = get_global_id(0);
    int index = g1 * data[0] * data[2] + g0 * data[2];
    int indexOut = g1*data[0]*4+g0*4;
    int i = 0;
    
    if (Image[indexOut + 3] == 255){
        for (i = 0; i < data[3]; i++){
            int tri[9];
            int i1 = 0;
            for (i1 = 0; i1 < 9; i1++){
                tri[i1] = triangles[i1+i*9];
            }
            float a = fabs((float)tri[0]*(tri[4]-tri[7]) + tri[3]*(tri[7]-tri[1]) + tri[6]* (tri[1]-tri[4]));
            float a1 = fabs((float)g0*(tri[4]-tri[7]) + tri[3]*(tri[7]-g1) + tri[6]* (g1-tri[4]));
            float a2 = fabs((float)tri[0]*(g1-tri[7]) + g0*(tri[7]-tri[1]) + tri[6]* (tri[1]-g1));
            float a3 = fabs((float)tri[0]*(tri[4]-g1) + tri[3]*(g1-tri[1]) + g0* (tri[1]-tri[4]));
            
            if(fabs((a1 + a2 + a3) -a) < 0.0001){
                int A = tri[2];
                int B = tri[5];
                int C = tri[8];
                float n = ((A*a1+B*a2+C*a3)/(a1+a2+a3))-data[5];
                if (data[6] == 0){
                    float o = n*(255/(data[4]-data[5]));
                    out[indexOut] = o;
                    out[indexOut+1] = o;
                    out[indexOut+2] = o;
                    out[indexOut+3] = 255;
                }
                else if (data[6] == 1){
                    float p = (data[4]-data[5])*0.25;
                    if (n >= p*2.7){
                        out[indexOut+1] = (((p*4)-n)/(p*1.3))*255;
                        out[indexOut] = 255;
                    }
                    else if (n >= p*2 && n < p*2.7){
                        out[indexOut] = ((n-p*2)/(p*0.7))*255;
                        out[indexOut+1] = 255;
                    }
                    else if (n >= p*1.3 && n < p*2){
                        out[indexOut+2] = ((2*p-n)/(p*0.7))*255;
                        out[indexOut+1] = 255;
                    }
                    if (n < p*1.3){
                        out[indexOut+1] = (n/(p*1.3))*255;
                        out[indexOut+2] = 255;
                    }
                    out[indexOut+3] = 255;
                }
                else if (data[6] == 2){
                    float p = (data[4]-data[5])*0.5;
                    if (n >= p){
                        out[indexOut] = 255;
                        out[indexOut+1] = (p*2-n)/p * 255;
                    }
                    else if (n < p){
                        out[indexOut+1] = 255;
                        out[indexOut] = (n)/p * 255;
                    }
                    out[indexOut+3] = 255;
                }
                else if (data[6] == 3){
                    float p = (data[4]-data[5])*0.5;
                    if (n > p){
                        out[indexOut] = 255;
                        out[indexOut+2] = (p*2-n)/p * 200;
                    }
                    else if (n < p){
                        out[indexOut+2] = 200;
                        out[indexOut] = n/p * 255;
                    }
                    out[indexOut+3] = 255;
                }
                break;
            }
        }
        if(out[indexOut+3] != 255){
            out[indexOut] = Image[indexOut];
            out[indexOut+1] = Image[indexOut+1];
            out[indexOut+2] = Image[indexOut+2];
            out[indexOut+3] = Image[indexOut+3];
        }
    }
}