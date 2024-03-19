#version 330 core

uniform mat4 ModelViewMatrix;
uniform mat4 ProjectionMatrix;

in vec3 Vertex;
in vec2 TexCoord;
in vec3 Color;

varying vec2 tex_coords;
varying vec4 color;
varying vec4 viewpos;
varying vec4 normal;

void main()
{
    //normal = gl_NormalMatrix * gl_Normal;
    // hack: using up vector only works on top surface of blocks
    // notice: there are issues with using modelViewMatrix instead of proper normalMatrix when doing non-uniform scale
    normal = ModelViewMatrix * vec4(0,1,0,0);

    color = vec4(Color,1.0);
    gl_Position = ProjectionMatrix * ModelViewMatrix * vec4(Vertex,1.0);
    tex_coords = TexCoord;
//    gl_TexCoord[0] = gl_MultiTexCoord0;

    // fog stuff (https://community.khronos.org/t/opengl-fog-and-shaders/52902)
//    vec4 eyePos = ModelViewMatrix * Vertex;
//    gl_FogFragCoord = abs(eyePos.z/eyePos.w);
    
    // more info for fragment shaders to play with
    viewpos = ModelViewMatrix * vec4(Vertex,1.0);
}
