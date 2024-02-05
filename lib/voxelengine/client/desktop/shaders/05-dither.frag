#version 130

varying vec4 color;
uniform sampler2D color_texture;

uniform float d;
uniform float e;

void main (void)
{
    vec4 tex_color = texture2D(color_texture, gl_TexCoord[0].st);
    //float test = dot(normal, vec3(0.0f,1.0f,0.0f));
    gl_FragColor = tex_color * (0.75 + 0.5 * vec4(color));
        
    // apply fog
    float fogFactor = pow((1-gl_Fog.color.a), gl_FogFragCoord);
    gl_FragColor = vec4(mix(gl_Fog.color.rgb, gl_FragColor.rgb, fogFactor), gl_FragColor.a);

    // raster stuff
    vec2 fc = floor(gl_FragCoord.xy / (1+10*e));
    vec2 f = fract(fc / int(2+100*d));
    float o = (0.3*f.x + 0.7*f.y - 0.5);
    
    // mix up signs to make less blocky
    vec2 s2 = sign(fract(fc/2)-0.49);
    float s = s2.x * s2.y;
    o *= s;
    
    // avoid bias to middle
    vec3 o3 = vec3(o,o,o);
    //vec3 omax = min(vec3(1.0) - gl_FragColor.xyz, gl_FragColor.xyz);
    //o3 = clamp( o3, -omax, omax);
    
    gl_FragColor.xyz += o3;
    gl_FragColor.xyz = round(gl_FragColor.xyz);
}
