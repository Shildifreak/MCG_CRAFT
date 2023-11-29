#version 130

varying vec4 color;
varying vec4 viewpos;
varying vec4 normal;

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
}
