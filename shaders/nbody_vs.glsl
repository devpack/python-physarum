#version 460 core

in vec4 in_position;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main() {
    //vec4 model_pos = m_model * vec4(in_position.xyz, 1.0);
	//vec4 view_model_pos = m_view * model_pos;
	//gl_Position = m_proj * view_model_pos;

	gl_Position = vec4(in_position.xyz, 1.0);
}