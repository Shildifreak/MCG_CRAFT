#version 130

varying vec4 color;
uniform sampler2D color_texture;

void main (void)
{
    gl_FragColor = texture2D(color_texture, gl_TexCoord[0].st);
}
