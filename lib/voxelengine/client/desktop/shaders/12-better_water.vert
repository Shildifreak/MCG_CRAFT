#version 130

varying vec4 color;
varying vec4 viewpos;
varying vec4 normal;

uniform int material;
uniform float time = 0;

uniform float height = 0.2;
uniform float speed = 0.1;

const vec4 yxzt_scale[] = vec4[](
    vec4(0.05, 0.2, -0.3, 1.5),
    vec4(0.04, 0.5, 0.5, 2),
    vec4(0.04, -0.51, -0.51, 2),
    vec4(0.015, 5.01, 0, 2.5),
    vec4(0.015, 5.5, 0, 2.3),
    vec4(0.015, 0, 3.02, 3),
    vec4(0.01, -4.24, 4.12, 5),
    vec4(0.001, 40.14, 40.13, 10)
);

float get_height(float x, float z) {
    float dy = 0;
    float sy_sum = 0;
    for (int i=0; i<yxzt_scale.length(); i++) {
        vec4 s = yxzt_scale[i];
        sy_sum += s[0]*5*height;
        dy     += s[0]*5*height *      sin(s[1]*x + s[2]*z + s[3]*10*speed*time);
    }
    return dy - sy_sum;
}

vec4 get_normal(float x, float z) {
    float dydx = 0;
    float dydz = 0;
    for (int i=0; i<yxzt_scale.length(); i++) {
        vec4 s = yxzt_scale[i];
        dydx   += s[0]*5*height * s[1]*cos(s[1]*x + s[2]*z + s[3]*10*speed*time);
        dydz   += s[0]*5*height * s[2]*cos(s[1]*x + s[2]*z + s[3]*10*speed*time);
    }
    return gl_ModelViewMatrix * vec4(dydx,1,dydz,0);
}


void main()
{
    //normal = gl_NormalMatrix * gl_Normal;
    // hack: using up vector only works on top surface of blocks
    // notice: there are issues with using modelViewMatrix instead of proper normalMatrix when doing non-uniform scale
    normal = gl_ModelViewMatrix * vec4(0,1,0,0);

    color = gl_Color;
    gl_Position = ftransform(); // fixed pipeline equivalent of gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
    gl_TexCoord[0] = gl_MultiTexCoord0;

    // fog stuff (https://community.khronos.org/t/opengl-fog-and-shaders/52902)
    vec4 eyePos = gl_ModelViewMatrix * gl_Vertex;
    gl_FogFragCoord = abs(eyePos.z/eyePos.w);
    
    // more info for fragment shaders to play with
    viewpos = gl_ModelViewMatrix * gl_Vertex;
    
    // water special
    if (material == MATERIAL(water)) {
        normal = get_normal(gl_Vertex.x, gl_Vertex.z);
        gl_Position.y += get_height(gl_Vertex.x, gl_Vertex.z);
    }
}
