/*
 * Copyright (C) 1999-2006  Brian Paul   All Rights Reserved.
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * BRIAN PAUL BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
 * AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */


/*
 * Brian Paul  26 January 2000
 * Adapted for PlayOnLinux usage by Quentin PÂRIS	03 march 2012
 * Built with gcc -lGL (-m32 for 32bits version)
 */

#define GLX_GLXEXT_PROTOTYPES

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <GL/gl.h>
#include <GL/glx.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>


#ifndef GLX_NONE_EXT
#define GLX_NONE_EXT  0x8000
#endif

#ifndef GLX_TRANSPARENT_RGB
#define GLX_TRANSPARENT_RGB 0x8008
#endif

#ifndef GLX_RGBA_BIT
#define GLX_RGBA_BIT			0x00000001
#endif

#ifndef GLX_COLOR_INDEX_BIT
#define GLX_COLOR_INDEX_BIT		0x00000002
#endif




static void print_screen_info(Display *dpy, GLboolean limits)
{
   int attribSingle[] = {
      GLX_RGBA,
      GLX_RED_SIZE, 1,
      GLX_GREEN_SIZE, 1,
      GLX_BLUE_SIZE, 1,
      None };
   int attribDouble[] = {
      GLX_RGBA,
      GLX_RED_SIZE, 1,
      GLX_GREEN_SIZE, 1,
      GLX_BLUE_SIZE, 1,
      GLX_DOUBLEBUFFER,
      None };

   GLXContext ctx = NULL;
   XVisualInfo *visinfo;

   /*
    * Find a basic GLX visual.  We'll then create a rendering context and
    * query various info strings.
    */
   visinfo = glXChooseVisual(dpy, 0, attribSingle);
   if (!visinfo)
      visinfo = glXChooseVisual(dpy, 0, attribDouble);

   if (visinfo)
      ctx = glXCreateContext( dpy, visinfo, NULL, True );

   if (!visinfo) {
      exit(2);
   }

   if (!ctx) {
      fprintf(stderr, "Error: glXCreateContext failed\n");
      XFree(visinfo);
      exit(2);
   }
     if (glXIsDirect(dpy, ctx)) {
        printf("64bits direct rendering is enabled\n");
	exit(0);
      } else {
        printf("64bits direct rendering is not enabled\n");
	exit(1);	
      }
   glXDestroyContext(dpy, ctx);
   XFree(visinfo);

}

int main(int argc, char *argv[])
{
   char *displayName = NULL;
   Display *dpy;
   dpy = XOpenDisplay(displayName);
   if (!dpy) {
      return -1;
   }
   /* Just want to see if direct rendering is supported on the main screen */
   print_screen_info(dpy, GL_FALSE);

   XCloseDisplay(dpy);

   return 0;
}
