#version 130

varying vec4 color;
varying vec4 viewpos;
varying vec4 normal;
uniform vec2 screenSize;
uniform sampler2D color_texture;
uniform sampler2D loopback;
uniform sampler2D loopback2;

uniform int material;

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
    vec4 loopColor2 = vec4(viewpos.xyz, 1);
    
    // output
    ivec2 st = ivec2(gl_FragCoord.st);
    vec4 outColor = texelFetch(loopback, st, 0);
    if (material == MATERIAL(water)) {
        outColor = vec4(0.5,0.7,1.0,1.0);
        vec4 startpos = texelFetch(loopback2, st, 0);
        vec4 viewDir = normalize(startpos - vec4(0,0,0,1));
        vec4 reflectDir = reflect(viewDir, normal);
        vec4 clippos = gl_ProjectionMatrix * (startpos + reflectDir);
        vec2 fragCoord2 = (0.5*clippos.xy/clippos.w + vec2(0.5,0.5)) * screenSize;
        vec2 st_dir = normalize(fragCoord2 - gl_FragCoord.st);
        for (int i = 10; i < 1080; i++) {
            ivec2 st2 = ivec2(st + st_dir*i);
            if (st2.y >= screenSize.y) {
                break;
            }
            vec4 pos = texelFetch(loopback2, st2, 0);
            vec4 direction = normalize(pos - startpos);
            if (dot(direction, normal) > dot(-viewDir, normal)) {
                outColor = texelFetch(loopback, st2, 0);
                break;
            }
        }
        fragColor.a = clamp(0, 1, 0.7-abs(-1.8*dot(viewDir, normal)));
//        fragColor.a *= fragColor.a;
    }
//    outColor.xyz = vec3(1/abs(texelFetch(loopback2, st, 0).z));
        
    gl_FragData[0] = vec4(outColor.xyz,fragColor.a);
    gl_FragData[1] = loopColor;
    gl_FragData[2] = loopColor2;
}
