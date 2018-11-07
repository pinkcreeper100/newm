#define _POSIX_C_SOURCE 200112L

#include "wm.h"

#include <assert.h>
#include <stdlib.h>
#include <unistd.h>
#include <wayland-server.h>
#include <wlr/backend.h>
#include <wlr/util/log.h>

#include "wm_server.h"

struct wm wm = { 0 };

void wm_init(){
    if(!wm.server) wm.server = calloc(1, sizeof(struct wm_server));
}

void wm_destroy(){
    if(!wm.server) return;

    wm_server_destroy(wm.server);
    free(wm.server);
    wm.server = 0;
}

void* run(void* ignore){
    if(!wm.server) return NULL;

    wlr_log_init(WLR_DEBUG, NULL);

    wm_server_init(wm.server);

    /* Setup socket and set env */
	const char *socket = wl_display_add_socket_auto(wm.server->wl_display);
	if (!socket) {
		wlr_log_errno(WLR_ERROR, "Unable to open wayland socket");
		wlr_backend_destroy(wm.server->wlr_backend);
		return NULL;
	}

	wlr_log(WLR_INFO, "Running compositor on wayland display '%s'", socket);
	setenv("_WAYLAND_DISPLAY", socket, true);

	if (!wlr_backend_start(wm.server->wlr_backend)) {
		wlr_log(WLR_ERROR, "Failed to start backend");
		wlr_backend_destroy(wm.server->wlr_backend);
		wl_display_destroy(wm.server->wl_display);
		return NULL;
	}

	setenv("WAYLAND_DISPLAY", socket, true);

    /* Main */
    wl_display_run(wm.server->wl_display);

    return NULL;
}

int wm_run(){
    if(!wm.server) return 2;

    pthread_create(&wm.thread, NULL, &run, NULL);

    return 0;
}

void wm_join(){
    if(!wm.server) return;

    pthread_join(wm.thread, NULL);
}



void wm_terminate(){
    if(!wm.server) return;

    wl_display_terminate(wm.server->wl_display);
    wm_join();
}
