#version 130

varying vec4 color;
varying vec4 viewpos;
uniform vec2 screenSize;
uniform sampler2D color_texture;
uniform sampler2D loopback;

uniform int material;
uniform float d;

vec4 blurred_fetch(int LOD) {
    vec2 texelpos = gl_FragCoord.st/(1<<LOD)-0.5;
    vec4 c00 = texelFetch(loopback, ivec2(texelpos)+ivec2(0,0), LOD);
    vec4 c01 = texelFetch(loopback, ivec2(texelpos)+ivec2(0,1), LOD);
    vec4 c10 = texelFetch(loopback, ivec2(texelpos)+ivec2(1,0), LOD);
    vec4 c11 = texelFetch(loopback, ivec2(texelpos)+ivec2(1,1), LOD);
    vec2 k = fract(texelpos);
    vec4 c0 = mix(c00, c01, k.y);
    vec4 c1 = mix(c10, c11, k.y);
    vec4 c = mix(c0, c1, k.x);
    return c;
}

void main (void)
{
    vec4 tex_color = texture2D(color_texture, gl_TexCoord[0].st);
    //float test = dot(normal, vec3(0.0f,1.0f,0.0f));
    vec4 fragColor = tex_color * (0.75 + 0.5 * vec4(color));
    
    // apply fog
    float fogFactor = pow((1-gl_Fog.color.a), gl_FogFragCoord);
    fragColor = vec4(mix(gl_Fog.color.rgb, fragColor.rgb, fogFactor), fragColor.a);

    // loopback
    vec4 loopColor = fragColor;
    
    vec4 outColor;
    int LOD = int(d * 10);
    if (material == MATERIAL(water)) {
        outColor = blurred_fetch(LOD);
        //outColor = vec4(0,0,1,1);
        fragColor.a = 1;
    }
    else {
        outColor = texelFetch(loopback, ivec2(gl_FragCoord.st), 0);
        //outColor = fragColor;
    }
        
    gl_FragData[0] = vec4(outColor.xyz,fragColor.a);
    gl_FragData[1] = loopColor;
}
