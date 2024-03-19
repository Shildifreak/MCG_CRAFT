#version 330 core

varying vec2 tex_coords;

varying vec4 color;
uniform sampler2D color_texture;

uniform int material;

void main (void)
{
    vec4 tex_color = texture2D(color_texture, tex_coords.st);
    //float test = dot(normal, vec3(0.0f,1.0f,0.0f));
    gl_FragColor = tex_color * (0.75 + 0.5 * vec4(color));
    
    if ((material == MATERIAL(transparent)) && (tex_color.a < 0.5)) {
        discard;
    }
    
    // apply fog
//    float fogFactor = pow((1-gl_Fog.color.a), gl_FogFragCoord);
//    gl_FragColor = vec4(mix(gl_Fog.color.rgb, gl_FragColor.rgb, fogFactor), gl_FragColor.a);
}
