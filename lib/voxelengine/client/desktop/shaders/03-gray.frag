#version 130

varying vec4 color;
uniform sampler2D color_texture;

void main (void)
{
    gl_FragColor = vec4(0.5);
}
