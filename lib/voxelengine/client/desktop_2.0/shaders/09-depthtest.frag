#version 130

varying vec4 color;
varying vec4 viewpos;
uniform sampler2D color_texture;

void main (void)
{
    vec4 tex_color = texture2D(color_texture, gl_TexCoord[0].st);
    //float test = dot(normal, vec3(0.0f,1.0f,0.0f));
    gl_FragColor = tex_color * (0.75 + 0.5 * vec4(color));
    
    // apply fog
    float fogFactor = pow((1-gl_Fog.color.a), gl_FogFragCoord);
    gl_FragColor = vec4(mix(gl_Fog.color.rgb, gl_FragColor.rgb, fogFactor), gl_FragColor.a);

    // show noise function
    float distance = 1 - pow(0.8, length(viewpos.xz)/10-2);
    distance = clamp(distance, 0, 1);

    //gl_FragColor.xyz = mix(vec3(0.5), vec3(0.95,0.95,1), distance);
    gl_FragColor.xyz = mix(vec3(0.3), vec3(1), distance);
    
    gl_FragColor.xyz += vec3(fwidth(tex_color)) * pow(0.2, length(viewpos.xz)/10);
}
