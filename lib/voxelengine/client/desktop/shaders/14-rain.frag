#version 130

varying vec4 color;
varying vec4 viewpos;
uniform sampler2D color_texture;
uniform vec2 screenSize;
uniform float time;

float rand(vec2 co){
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main (void)
{
    vec4 tex_color = texture2D(color_texture, gl_TexCoord[0].st);
    //float test = dot(normal, vec3(0.0f,1.0f,0.0f));
    gl_FragColor = tex_color * (0.75 + 0.5 * vec4(color));
    
    // apply fog
    float fogFactor = pow((1-gl_Fog.color.a), gl_FogFragCoord);
    gl_FragColor = vec4(mix(gl_Fog.color.rgb, gl_FragColor.rgb, fogFactor), gl_FragColor.a);

    // calculate depth
    float distance = 1 - pow(0.8, length(viewpos.xz)/10-0.05);
    distance = clamp(distance, 0, 1);

    // direction of rain
    vec4 d = gl_ModelViewMatrix * vec4(0.3*sin(time*0.011),0.9,0.3*sin(time*0.03),0);
    
    // calculate noise
    //float n = rand(ivec2((st + vec2(0,1000*time*d.y))/vec2(3,100*d.y)).xy/100.0)*d.y;
    vec2 offset = vec2(0, 2*time);
    float n = 0;
    for (int i=0; i<10; i++) {
        float dxi = 0.01*sin(i+time);
        vec2 st = (d.y*gl_FragCoord.st - gl_FragCoord.ts*(d.x+dxi)) / screenSize;
        float r = 0.5*(1+rand(ivec2((st + offset*(1+i/10.))*vec2(100,5)*(i+1.)).xy/100.0));
        if (10*distance > i-r*2+2) {
            n += 0.5*(1-n) * r;
        }
    }
    
    gl_FragColor.xyz = mix(tex_color.xyz, vec3(0.5,0.7,1.0), n);
    
    if ((fract(time*10) < 0.0001) && !bool(int(time)&31)) {
        gl_FragColor.xyz = vec3(1);
    }
    
    //gl_FragColor.xyz += vec3(fwidth(tex_color)) * pow(0.2, length(viewpos.xz)/10);
}
