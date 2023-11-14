#version 130

varying vec4 color;
uniform vec2 screenSize;
uniform sampler2D color_texture;
uniform sampler2D loopback;

void main (void)
{
    vec4 tex_color = texture2D(color_texture, gl_TexCoord[0].st);
    //float test = dot(normal, vec3(0.0f,1.0f,0.0f));
    vec4 fragColor = tex_color * (0.75 + 0.5 * vec4(color));
    
    // apply fog
    float fogFactor = pow((1-gl_Fog.color.a), gl_FogFragCoord);
    fragColor = vec4(mix(gl_Fog.color.rgb, fragColor.rgb, fogFactor), fragColor.a);

    // loopback
    vec2 smearing = vec2(-1,-2);
    //vec4 loopbackColor = texture2D(loopback, (gl_FragCoord.st+smearing)/screenSize);
    int LOD = 3;
    vec4 loopbackColor = texelFetch(loopback, ivec2((gl_FragCoord.st+smearing)/(1<<LOD)), LOD);
    
    vec4 loopColor = mix(loopbackColor, fragColor, 0.03);
    
    vec2 offset = vec2(-100, 0);
    vec4 loopbackColorL = texelFetch(loopback, ivec2((gl_FragCoord.st+smearing-offset)/(1<<LOD)), LOD);
    vec4 loopbackColorR = texelFetch(loopback, ivec2((gl_FragCoord.st+smearing+offset)/(1<<LOD)), LOD);
    vec4 outColor = mix(loopbackColorL, loopbackColorR, (gl_FragCoord.s+offset.x)/(screenSize.x+2*offset.x));
    
    gl_FragData[0] = vec4(outColor.xyz,fragColor.a);
    gl_FragData[1] = loopColor;
}
