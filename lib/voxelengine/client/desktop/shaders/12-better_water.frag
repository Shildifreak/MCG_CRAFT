#version 130

varying vec4 color;
varying vec4 viewpos;
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
//        vec4 nextpos = texelFetch(loopback2, st + ivec2(0,10), 0);
//        vec3 direction = normalize(nextpos.xyz-startpos.xyz);
//        outColor.xyz = vec3(abs(normalize(nextpos.xyz-startpos.xyz)).z);
        vec3 direction = normalize(dFdy(startpos.xyz));
        for (int i = 10; i < 2000; i++) {
            if (st.y + i >= screenSize.y) {
                break;
            }
            vec4 pos = texelFetch(loopback2, st + ivec2(0,i), 0);
            vec3 reflectDir = normalize(pos.xyz-startpos.xyz);
            if (dot(reflectDir, direction) < dot(normalize(startpos.xyz-vec3(0,0,0)), direction)) {
                outColor = texelFetch(loopback, st + ivec2(0,i), 0);
                break;
            }
        }
//        fragColor.a = 1;
    }
//    outColor.xyz = vec3(1/abs(texelFetch(loopback2, st, 0).z));
        
    gl_FragData[0] = vec4(outColor.xyz,fragColor.a);
    gl_FragData[1] = loopColor;
    gl_FragData[2] = loopColor2;
}
