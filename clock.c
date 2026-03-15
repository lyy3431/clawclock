/*
 * ClawClock - A graphical clock application for Linux (C version using GTK3)
 * Supports analog and digital time display with timezone configuration
 */

#include <gtk/gtk.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>

#define M_PI 3.14159265358979323846

// Colors
#define BG_COLOR "#1a1a2e"
#define FACE_COLOR "#16213e"
#define HAND_COLOR "#e94560"
#define TEXT_COLOR "#ffffff"
#define SECOND_COLOR "#ff6b6b"

// Global variables
typedef struct {
    GtkWidget *drawing_area;
    GtkWidget *digital_label;
    GtkWidget *date_label;
    GtkWidget *tz_combo;
    GtkWidget *mode_combo;
    gchar timezone[64];
    gint mode; // 0=analog, 1=digital, 2=both
    gint width;
    gint height;
} ClockData;

static gint current_hour = 0;
static gint current_minute = 0;
static gint current_second = 0;

// Get timezone offset in hours
static gdouble get_timezone_offset(const gchar *tz_name) {
    if (strcmp(tz_name, "UTC") == 0) return 0.0;
    if (strcmp(tz_name, "Asia/Shanghai") == 0) return 8.0;
    if (strcmp(tz_name, "Asia/Tokyo") == 0) return 9.0;
    if (strcmp(tz_name, "Asia/Seoul") == 0) return 9.0;
    if (strcmp(tz_name, "America/New_York") == 0) return -5.0;
    if (strcmp(tz_name, "America/Los_Angeles") == 0) return -8.0;
    if (strcmp(tz_name, "Europe/London") == 0) return 0.0;
    if (strcmp(tz_name, "Europe/Paris") == 0) return 1.0;
    if (strcmp(tz_name, "Australia/Sydney") == 0) return 11.0;
    return 8.0; // default Shanghai
}

// Get current time with timezone
static void get_current_time(const gchar *tz_name, gint *hour, gint *minute, gint *second) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    
    gdouble offset = get_timezone_offset(tz_name);
    
    *hour = (tm_info->tm_hour + (gint)offset) % 24;
    if (*hour < 0) *hour += 24;
    *minute = tm_info->tm_min;
    *second = tm_info->tm_sec;
}

// Draw clock face
static gboolean draw_clock(GtkWidget *widget, cairo_t *cr, gpointer data) {
    ClockData *clock_data = (ClockData *)data;
    
    gint width = gtk_widget_get_allocated_width(widget);
    gint height = gtk_widget_get_allocated_height(widget);
    gint cx = width / 2;
    gint cy = height / 2;
    gint r = MIN(width, height) / 2 - 20;
    
    // Background
    cairo_set_source_hex_color(cr, FACE_COLOR);
    cairo_paint(cr);
    
    // Clock face circle
    cairo_set_source_hex_color(cr, HAND_COLOR);
    cairo_set_line_width(cr, 3);
    cairo_arc(cr, cx, cy, r, 0, 2 * M_PI);
    cairo_stroke(cr);
    
    // Hour marks
    cairo_set_source_hex_color(cr, TEXT_COLOR);
    cairo_set_line_width(cr, 2);
    for (gint i = 0; i < 12; i++) {
        gdouble angle = (i * 30 - 90) * M_PI / 180;
        gdouble x1 = cx + (r - 15) * cos(angle);
        gdouble y1 = cy + (r - 15) * sin(angle);
        gdouble x2 = cx + (r - 5) * cos(angle);
        gdouble y2 = cy + (r - 5) * sin(angle);
        cairo_move_to(cr, x1, y1);
        cairo_line_to(cr, x2, y2);
        cairo_stroke(cr);
    }
    
    // Minute marks
    cairo_set_line_width(cr, 1);
    for (gint i = 0; i < 60; i++) {
        if (i % 5 != 0) {
            gdouble angle = (i * 6 - 90) * M_PI / 180;
            gdouble x1 = cx + (r - 10) * cos(angle);
            gdouble y1 = cy + (r - 10) * sin(angle);
            gdouble x2 = cx + (r - 5) * cos(angle);
            gdouble y2 = cy + (r - 5) * sin(angle);
            cairo_move_to(cr, x1, y1);
            cairo_line_to(cr, x2, y2);
            cairo_stroke(cr);
        }
    }
    
    // Center dot
    cairo_set_source_hex_color(cr, HAND_COLOR);
    cairo_arc(cr, cx, cy, 5, 0, 2 * M_PI);
    cairo_fill(cr);
    
    // Draw hands
    get_current_time(clock_data->timezone, &current_hour, &current_minute, &current_second);
    
    // Second hand
    gdouble sec_angle = (current_second * 6 - 90) * M_PI / 180;
    gdouble sec_len = r - 20;
    cairo_set_source_hex_color(cr, SECOND_COLOR);
    cairo_set_line_width(cr, 2);
    cairo_move_to(cr, cx, cy);
    cairo_line_to(cr, cx + sec_len * cos(sec_angle), cy + sec_len * sin(sec_angle));
    cairo_stroke(cr);
    
    // Minute hand
    gdouble min_angle = (current_minute * 6 - 90) * M_PI / 180;
    gdouble min_len = r - 30;
    cairo_set_source_hex_color(cr, TEXT_COLOR);
    cairo_set_line_width(cr, 4);
    cairo_move_to(cr, cx, cy);
    cairo_line_to(cr, cx + min_len * cos(min_angle), cy + min_len * sin(min_angle));
    cairo_stroke(cr);
    
    // Hour hand
    gdouble hour_angle = ((current_hour % 12 + current_minute / 60.0) * 30 - 90) * M_PI / 180;
    gdouble hour_len = r - 60;
    cairo_set_source_hex_color(cr, HAND_COLOR);
    cairo_set_line_width(cr, 6);
    cairo_move_to(cr, cx, cy);
    cairo_line_to(cr, cx + hour_len * cos(hour_angle), cy + hour_len * sin(hour_angle));
    cairo_stroke(cr);
    
    return FALSE;
}

// Update digital display
static void update_digital(ClockData *data) {
    get_current_time(data->timezone, &current_hour, &current_minute, &current_second);
    
    gchar time_str[32];
    gchar date_str[128];
    
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    
    g_snprintf(time_str, sizeof(time_str), "%02d:%02d:%02d", 
               current_hour, current_minute, current_second);
    
    g_snprintf(date_str, sizeof(date_str), "%04d-%02d-%02d %s\n%s",
               tm_info->tm_year + 1900, tm_info->tm_mon + 1, tm_info->tm_mday,
               tm_info->tm_wday == 0 ? "Sunday" :
               tm_info->tm_wday == 1 ? "Monday" :
               tm_info->tm_wday == 2 ? "Tuesday" :
               tm_info->tm_wday == 3 ? "Wednesday" :
               tm_info->tm_wday == 4 ? "Thursday" :
               tm_info->tm_wday == 5 ? "Friday" : "Saturday",
               data->timezone);
    
    gtk_label_set_text(GTK_LABEL(data->digital_label), time_str);
    gtk_label_set_text(GTK_LABEL(data->date_label), date_str);
}

// Timeout callback
static gboolean timeout_callback(gpointer data) {
    ClockData *clock_data = (ClockData *)data;
    
    if (clock_data->mode == 0 || clock_data->mode == 2) {
        gtk_widget_queue_draw(clock_data->drawing_area);
    }
    
    if (clock_data->mode == 1 || clock_data->mode == 2) {
        update_digital(clock_data);
    }
    
    return TRUE;
}

// Timezone changed callback
static void on_timezone_changed(GtkComboBox *widget, gpointer data) {
    ClockData *clock_data = (ClockData *)data;
    gint active = gtk_combo_box_get_active(widget);
    const gchar *timezones[] = {
        "Asia/Shanghai", "America/New_York", "America/Los_Angeles",
        "Europe/London", "Europe/Paris", "Asia/Tokyo", "Asia/Seoul",
        "Australia/Sydney", "UTC"
    };
    g_strlcpy(clock_data->timezone, timezones[active], sizeof(clock_data->timezone));
}

// Mode changed callback
static void on_mode_changed(GtkComboBox *widget, gpointer data) {
    ClockData *clock_data = (ClockData *)data;
    clock_data->mode = gtk_combo_box_get_active(widget);
}

int main(int argc, char *argv[]) {
    gtk_init(&argc, &argv);
    
    // Create window
    GtkWidget *window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "ClawClock");
    gtk_window_set_default_size(GTK_WINDOW(window), 600, 500);
    gtk_container_set_border_width(GTK_CONTAINER(window), 10);
    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);
    
    // Main container
    GtkWidget *main_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_container_add(GTK_CONTAINER(window), main_box);
    
    // Clock data
    ClockData *clock_data = g_malloc(sizeof(ClockData));
    g_strlcpy(clock_data->timezone, "Asia/Shanghai", sizeof(clock_data->timezone));
    clock_data->mode = 2; // both
    clock_data->width = 300;
    clock_data->height = 300;
    
    // Control box
    GtkWidget *control_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 10);
    gtk_box_pack_start(GTK_BOX(main_box), control_box, FALSE, FALSE, 5);
    
    // Timezone label
    GtkWidget *tz_label = gtk_label_new("Timezone:");
    gtk_box_pack_start(GTK_BOX(control_box), tz_label, FALSE, FALSE, 5);
    
    // Timezone combo
    const gchar *timezones[] = {
        "Asia/Shanghai", "America/New_York", "America/Los_Angeles",
        "Europe/London", "Europe/Paris", "Asia/Tokyo", "Asia/Seoul",
        "Australia/Sydney", "UTC"
    };
    
    clock_data->tz_combo = gtk_combo_box_text_new();
    for (gint i = 0; i < 9; i++) {
        gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(clock_data->tz_combo), timezones[i]);
    }
    gtk_combo_box_set_active(GTK_COMBO_BOX(clock_data->tz_combo), 0);
    g_signal_connect(clock_data->tz_combo, "changed", G_CALLBACK(on_timezone_changed), clock_data);
    gtk_box_pack_start(GTK_BOX(control_box), clock_data->tz_combo, FALSE, FALSE, 5);
    
    // Mode label
    GtkWidget *mode_label = gtk_label_new("  Mode:");
    gtk_box_pack_start(GTK_BOX(control_box), mode_label, FALSE, FALSE, 5);
    
    // Mode combo
    clock_data->mode_combo = gtk_combo_box_text_new();
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(clock_data->mode_combo), "Analog");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(clock_data->mode_combo), "Digital");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(clock_data->mode_combo), "Both");
    gtk_combo_box_set_active(GTK_COMBO_BOX(clock_data->mode_combo), 2);
    g_signal_connect(clock_data->mode_combo, "changed", G_CALLBACK(on_mode_changed), clock_data);
    gtk_box_pack_start(GTK_BOX(control_box), clock_data->mode_combo, FALSE, FALSE, 5);
    
    // Content box (horizontal)
    GtkWidget *content_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 10);
    gtk_box_pack_start(GTK_BOX(main_box), content_box, TRUE, TRUE, 5);
    
    // Drawing area for analog clock
    clock_data->drawing_area = gtk_drawing_area_new();
    gtk_widget_set_size_request(clock_data->drawing_area, 300, 300);
    g_signal_connect(clock_data->drawing_area, "draw", G_CALLBACK(draw_clock), clock_data);
    gtk_box_pack_start(GTK_BOX(content_box), clock_data->drawing_area, TRUE, TRUE, 5);
    
    // Digital display box
    GtkWidget *digital_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_box_pack_start(GTK_BOX(content_box), digital_box, TRUE, TRUE, 5);
    
    // Digital time label
    clock_data->digital_label = gtk_label_new("00:00:00");
    PangoAttrList *attrs = pango_attr_list_new();
    PangoAttribute *attr = pango_attr_size_new(36 * PANGO_SCALE);
    pango_attr_list_insert(attrs, attr);
    PangoFontDescription *desc = pango_font_description_from_string("Courier New Bold 36");
    gtk_widget_override_font(clock_data->digital_label, desc);
    gtk_label_set_attributes(GTK_LABEL(clock_data->digital_label), attrs);
    gtk_box_pack_start(GTK_BOX(digital_box), clock_data->digital_label, TRUE, TRUE, 5);
    
    // Date label
    clock_data->date_label = gtk_label_new("");
    gtk_label_set_justify(GTK_LABEL(clock_data->date_label), GTK_JUSTIFY_CENTER);
    gtk_box_pack_start(GTK_BOX(digital_box), clock_data->date_label, FALSE, FALSE, 5);
    
    // Apply dark theme
    GdkCssProvider *provider = gdk_css_provider_new();
    gdk_css_provider_load_from_data(provider,
        "window { background-color: " BG_COLOR "; }"
        "label { color: " TEXT_COLOR "; }",
        -1, NULL);
    gtk_style_context_add_provider_for_screen(gdk_screen_get_default(),
        GTK_STYLE_PROVIDER(provider), GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    
    // Show all
    gtk_widget_show_all(window);
    
    // Start timeout (50ms)
    g_timeout_add(50, timeout_callback, clock_data);
    
    // Run
    gtk_main();
    
    g_free(clock_data);
    return 0;
}