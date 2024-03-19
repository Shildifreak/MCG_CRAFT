#version 130

varying vec4 color;
uniform sampler2D color_texture;

void main (void)
{
    vec4 tex_color = texture2D(color_texture, gl_TexCoord[0].st);
    //float test = dot(normal, vec3(0.0f,1.0f,0.0f));
    gl_FragColor = tex_color * (0.75 + 0.5 * vec4(color));
        
    // apply fog
    float fogFactor = pow((1-gl_Fog.color.a), gl_FogFragCoord);
    gl_FragColor = vec4(mix(gl_Fog.color.rgb, gl_FragColor.rgb, fogFactor), gl_FragColor.a);

    // apply grayscale (magic numbers from https://www.youtube.com/watch?v=fv-wlo8yVhk)
    gl_FragColor.xyz = vec3(dot(gl_FragColor.xyz, vec3(0.21,0.72,0.07)));
}
