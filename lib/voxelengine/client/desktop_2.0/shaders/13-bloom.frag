#version 130

varying vec4 color;
varying vec4 viewpos;
uniform vec2 screenSize;
uniform sampler2D color_texture;
uniform sampler2D loopback;

uniform int material;
uniform float d;

vec4 clampedTexelFetch(sampler2D texture, ivec2 position, int LOD) {
    ivec2 clampedPosition = clamp(position, ivec2(1,1), (ivec2(screenSize)>>LOD)-1);
    return texelFetch(texture, clampedPosition, LOD);
}

vec4 blurred_fetch2(int LOD, vec2 offset) {
    vec2 texelpos = gl_FragCoord.st/(1<<LOD)-0.5 + offset;
    vec4 c00 = clampedTexelFetch(loopback, ivec2(texelpos)+ivec2(0,0), LOD);
    vec4 c01 = clampedTexelFetch(loopback, ivec2(texelpos)+ivec2(0,1), LOD);
    vec4 c10 = clampedTexelFetch(loopback, ivec2(texelpos)+ivec2(1,0), LOD);
    vec4 c11 = clampedTexelFetch(loopback, ivec2(texelpos)+ivec2(1,1), LOD);
    vec2 k = fract(texelpos);
    vec4 c0 = mix(c00, c01, k.y);
    vec4 c1 = mix(c10, c11, k.y);
    vec4 c = mix(c0, c1, k.x);
    return c;
}

vec4 blurred_fetch(int LOD) {
    return (
        (1/16.) * blurred_fetch2(LOD, 1*vec2(-1,-1)) + 
        (1/ 8.) * blurred_fetch2(LOD, 1*vec2(-1, 0)) +
        (1/16.) * blurred_fetch2(LOD, 1*vec2(-1, 1)) +
        (1/ 8.) * blurred_fetch2(LOD, 1*vec2( 0,-1)) +
        (1/ 4.) * blurred_fetch2(LOD, 1*vec2( 0, 0)) +
        (1/ 8.) * blurred_fetch2(LOD, 1*vec2( 0, 1)) +
        (1/16.) * blurred_fetch2(LOD, 1*vec2( 1,-1)) +
        (1/ 8.) * blurred_fetch2(LOD, 1*vec2( 1, 0)) +
        (1/16.) * blurred_fetch2(LOD, 1*vec2( 1, 1)) );
}

vec4 blurred_fetch(float LOD) {
    vec4 c0 = blurred_fetch(int(LOD));
    vec4 c1 = blurred_fetch(int(LOD)+1);
    float k = fract(LOD);
    vec4  c = mix(c0, c1, k);
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
    vec4 loopColor = vec4(0);
    if (material == MATERIAL(glowing)) {
        if (length(fragColor.rgb)*length(fragColor.rgb) > 0.5) {
            loopColor = 100*fragColor*fragColor;
        }
    }

    // output
    float LOD = d * 10;
    vec4 light = blurred_fetch(LOD);
    vec3 outColor = fragColor.rgb; //texelFetch(loopback, ivec2(gl_FragCoord.st), 0).rgb;
    outColor *= 0.05*light.rgb + 1;
    //outColor = clamp(outColor, 0, 1);
        
    gl_FragData[0] = vec4(outColor, fragColor.a);
    gl_FragData[1] = loopColor;
}
