#include <stdio.h>
#include <GL/glut.h> 

// Built with gcc -o x86.check -m32 -lGL -lGLU -lX11 -lXmu -lXi -lm
int main(void)
{
	printf("OpenGL 32bits is working\n");
	return 0;
}
