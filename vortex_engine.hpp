// ============================================================================
// Vortex3D Engine Runtime - Single-Header High-Performance 3D Game Core
// Architecture: Native Win32 + OpenGL Hardware-Accelerated 3D Pipeline
// Zero external dependency: links directly with -lopengl32 -lgdi32 -luser32 -lwinmm
// ============================================================================
#ifndef VORTEX_ENGINE_HPP
#define VORTEX_ENGINE_HPP

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <mmsystem.h>
#include <GL/gl.h>
#include <cmath>
#include <vector>
#include <string>
#include <iostream>
#include <chrono>
#include <functional>
#include <memory>
#include <algorithm>

#pragma comment(lib, "opengl32.lib")
#pragma comment(lib, "gdi32.lib")
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "winmm.lib")

namespace vortex {

// ----------------------------------------------------------------------------
// 1. Math Primitives
// ----------------------------------------------------------------------------
struct vec3 {
    float x = 0.0f, y = 0.0f, z = 0.0f;
    vec3() : x(0), y(0), z(0) {}
    vec3(float _x, float _y, float _z) : x(_x), y(_y), z(_z) {}

    vec3 operator+(const vec3& o) const { return vec3(x + o.x, y + o.y, z + o.z); }
    vec3 operator-(const vec3& o) const { return vec3(x - o.x, y - o.y, z - o.z); }
    vec3 operator*(float s) const { return vec3(x * s, y * s, z * s); }
    vec3 operator/(float s) const { return (s != 0.0f) ? vec3(x / s, y / s, z / s) : vec3(); }
    vec3& operator+=(const vec3& o) { x += o.x; y += o.y; z += o.z; return *this; }
    vec3& operator-=(const vec3& o) { x -= o.x; y -= o.y; z -= o.z; return *this; }

    float length() const { return std::sqrt(x * x + y * y + z * z); }
    float length_sq() const { return x * x + y * y + z * z; }
    vec3 normalized() const {
        float l = length();
        return (l > 0.0001f) ? (*this / l) : vec3(0, 0, 0);
    }
    static float distance(const vec3& a, const vec3& b) {
        return (a - b).length();
    }
    static vec3 lerp(const vec3& a, const vec3& b, float t) {
        return a + (b - a) * t;
    }
};

struct color {
    float r = 1.0f, g = 1.0f, b = 1.0f, a = 1.0f;
    color() : r(1), g(1), b(1), a(1) {}
    color(float _r, float _g, float _b, float _a = 1.0f) : r(_r), g(_g), b(_b), a(_a) {}

    color operator*(float s) const { return color(r * s, g * s, b * s, a); }

    static color rgb(float r, float g, float b) { return color(r, g, b, 1.0f); }
    static color rgba(float r, float g, float b, float a) { return color(r, g, b, a); }
    static color red()     { return color(1.0f, 0.2f, 0.2f); }
    static color green()   { return color(0.2f, 1.0f, 0.3f); }
    static color blue()    { return color(0.2f, 0.4f, 1.0f); }
    static color cyan()    { return color(0.0f, 0.9f, 1.0f); }
    static color magenta() { return color(1.0f, 0.1f, 0.8f); }
    static color yellow()  { return color(1.0f, 0.9f, 0.1f); }
    static color white()   { return color(1.0f, 1.0f, 1.0f); }
    static color black()   { return color(0.0f, 0.0f, 0.0f); }
    static color dark_gray(){ return color(0.12f, 0.12f, 0.15f); }
};

struct transform {
    vec3 position = vec3(0, 0, 0);
    vec3 rotation = vec3(0, 0, 0); // Euler degrees (pitch, yaw, roll)
    vec3 scale    = vec3(1, 1, 1);
};

// ----------------------------------------------------------------------------
// 2. Materials & Lighting
// ----------------------------------------------------------------------------
struct Material {
    color albedo = color::white();
    float metallic = 0.0f;
    float roughness = 0.5f;
    color emission = color::black();
    bool wireframe = false;
};

struct Light {
    vec3 position = vec3(0, 10, 0);
    color diffuse = color(1.0f, 0.95f, 0.85f);
    float intensity = 1.0f;
    float radius = 50.0f;
};

struct Camera {
    vec3 position = vec3(0, 5, 10);
    vec3 target   = vec3(0, 1, 0);
    float fov     = 65.0f;
    float near_z  = 0.1f;
    float far_z   = 500.0f;
    float pitch   = 15.0f;
    float yaw     = 0.0f;
};

// ----------------------------------------------------------------------------
// 3. Particle System
// ----------------------------------------------------------------------------
struct Particle {
    vec3 position;
    vec3 velocity;
    color tint;
    float size;
    float life;
    float max_life;
};

class ParticleEmitter {
public:
    std::vector<Particle> particles;
    vec3 position;
    color base_color = color::cyan();
    float rate = 20.0f;
    bool active = true;

    void burst(vec3 origin, int count, color tint, float speed = 10.0f, float life = 0.8f) {
        for (int i = 0; i < count; ++i) {
            Particle p;
            p.position = origin;
            float theta = ((rand() % 360) * 3.14159f) / 180.0f;
            float phi = (((rand() % 180) - 90) * 3.14159f) / 180.0f;
            float spd = speed * (0.5f + ((rand() % 100) / 100.0f));
            p.velocity = vec3(std::cos(phi) * std::cos(theta), std::sin(phi), std::cos(phi) * std::sin(theta)) * spd;
            p.tint = tint;
            p.size = 0.15f + ((rand() % 10) / 40.0f);
            p.life = life * (0.6f + ((rand() % 100) / 100.0f));
            p.max_life = p.life;
            particles.push_back(p);
        }
    }

    void update(float dt) {
        for (auto it = particles.begin(); it != particles.end();) {
            it->life -= dt;
            if (it->life <= 0.0f) {
                it = particles.erase(it);
            } else {
                it->position += it->velocity * dt;
                it->velocity.y -= 9.8f * dt * 0.25f; // Gentle gravity on particles
                ++it;
            }
        }
    }

    void render() {
        glDisable(GL_LIGHTING);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE); // Additive blending for glowing particles

        for (const auto& p : particles) {
            float alpha = (p.life / p.max_life);
            glColor4f(p.tint.r, p.tint.g, p.tint.b, alpha);

            glPushMatrix();
            glTranslatef(p.position.x, p.position.y, p.position.z);
            float s = p.size * alpha;

            glBegin(GL_QUADS);
            glVertex3f(-s, -s, 0);
            glVertex3f( s, -s, 0);
            glVertex3f( s,  s, 0);
            glVertex3f(-s,  s, 0);
            glEnd();

            glPopMatrix();
        }

        glDisable(GL_BLEND);
        glEnable(GL_LIGHTING);
    }
};

// ----------------------------------------------------------------------------
// 4. Entity & Physics
// ----------------------------------------------------------------------------
enum class MeshType { CUBE, SPHERE, CYLINDER, LASER, ARENA_FLOOR, PILLAR };

struct Entity {
    int id = 0;
    std::string tag = "default";
    transform tr;
    vec3 velocity = vec3(0, 0, 0);
    MeshType mesh_type = MeshType::CUBE;
    Material mat;
    float bounding_radius = 1.0f;
    bool has_rigidbody = false;
    bool use_gravity = false;
    bool is_grounded = false;
    bool is_alive = true;
    float health = 100.0f;
    float max_health = 100.0f;
    float custom_timer = 0.0f;
};

// ----------------------------------------------------------------------------
// 5. HUD System
// ----------------------------------------------------------------------------
struct HUD {
    float player_health = 100.0f;
    int score = 0;
    int wave = 1;
    bool game_over = false;

    void draw(int width, int height) {
        glDisable(GL_LIGHTING);
        glDisable(GL_DEPTH_TEST);

        glMatrixMode(GL_PROJECTION);
        glPushMatrix();
        glLoadIdentity();
        glOrtho(0, width, height, 0, -1, 1);

        glMatrixMode(GL_MODELVIEW);
        glPushMatrix();
        glLoadIdentity();

        // 1. Crosshair in center
        float cx = width * 0.5f;
        float cy = height * 0.5f;
        glColor4f(0.0f, 1.0f, 0.8f, 0.85f);
        glLineWidth(2.0f);
        glBegin(GL_LINES);
        glVertex2f(cx - 12, cy); glVertex2f(cx - 4, cy);
        glVertex2f(cx + 4, cy);  glVertex2f(cx + 12, cy);
        glVertex2f(cx, cy - 12); glVertex2f(cx, cy - 4);
        glVertex2f(cx, cy + 4);  glVertex2f(cx, cy + 12);
        glEnd();

        // 2. Health Bar (top left)
        float bar_x = 30, bar_y = 30, bar_w = 260, bar_h = 22;
        // Background
        glColor4f(0.1f, 0.1f, 0.15f, 0.8f);
        glBegin(GL_QUADS);
        glVertex2f(bar_x, bar_y);
        glVertex2f(bar_x + bar_w, bar_y);
        glVertex2f(bar_x + bar_w, bar_y + bar_h);
        glVertex2f(bar_x, bar_y + bar_h);
        glEnd();

        // Foreground Health
        float pct = std::max(0.0f, std::min(1.0f, player_health / 100.0f));
        glColor4f(1.0f - pct, pct * 0.9f, 0.2f, 1.0f);
        glBegin(GL_QUADS);
        glVertex2f(bar_x + 2, bar_y + 2);
        glVertex2f(bar_x + 2 + (bar_w - 4) * pct, bar_y + 2);
        glVertex2f(bar_x + 2 + (bar_w - 4) * pct, bar_y + bar_h - 2);
        glVertex2f(bar_x + 2, bar_y + bar_h - 2);
        glEnd();

        // Health Bar Border
        glColor4f(0.0f, 0.9f, 1.0f, 0.9f);
        glBegin(GL_LINE_LOOP);
        glVertex2f(bar_x, bar_y);
        glVertex2f(bar_x + bar_w, bar_y);
        glVertex2f(bar_x + bar_w, bar_y + bar_h);
        glVertex2f(bar_x, bar_y + bar_h);
        glEnd();

        // 3. Score Indicators
        float score_bar_x = width - 200.0f;
        glColor4f(1.0f, 0.85f, 0.1f, 0.9f);
        glBegin(GL_QUADS);
        glVertex2f(score_bar_x, 30);
        glVertex2f(score_bar_x + 160, 30);
        glVertex2f(score_bar_x + 160, 52);
        glVertex2f(score_bar_x, 52);
        glEnd();

        // 4. Game Over Screen Overlay
        if (game_over) {
            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
            glColor4f(0.05f, 0.0f, 0.02f, 0.75f);
            glBegin(GL_QUADS);
            glVertex2f(0, 0);
            glVertex2f((float)width, 0);
            glVertex2f((float)width, (float)height);
            glVertex2f(0, (float)height);
            glEnd();
            glDisable(GL_BLEND);

            // Red warning banner
            glColor4f(1.0f, 0.1f, 0.1f, 0.9f);
            glBegin(GL_QUADS);
            glVertex2f(cx - 220, cy - 40);
            glVertex2f(cx + 220, cy - 40);
            glVertex2f(cx + 220, cy + 40);
            glVertex2f(cx - 220, cy + 40);
            glEnd();
        }

        glMatrixMode(GL_PROJECTION);
        glPopMatrix();
        glMatrixMode(GL_MODELVIEW);
        glPopMatrix();

        glEnable(GL_DEPTH_TEST);
        glEnable(GL_LIGHTING);
    }
};

// ----------------------------------------------------------------------------
// 6. Engine Application Core
// ----------------------------------------------------------------------------
class Engine {
public:
    static Engine& instance() {
        static Engine eng;
        return eng;
    }

    HWND hwnd = nullptr;
    HDC hdc = nullptr;
    HGLRC hglrc = nullptr;
    int width = 1280;
    int height = 720;
    bool running = true;
    float fps_cap = 120.0f;

    // Game state
    Camera main_camera;
    std::vector<Entity> entities;
    ParticleEmitter particles;
    HUD hud;
    Light sun;
    color ambient_light = color(0.12f, 0.14f, 0.2f);
    color fog_color = color(0.08f, 0.09f, 0.14f);
    bool fog_enabled = true;

    // Input state
    bool keys[256] = {false};
    bool keys_prev[256] = {false};
    bool mouse_left = false;
    bool mouse_left_prev = false;
    int mouse_x = 0, mouse_y = 0;
    int mouse_dx = 0, mouse_dy = 0;

    // Callbacks
    std::function<void()> on_start_fn;
    std::function<void(float)> on_update_fn;
    std::function<void(Entity&, Entity&)> on_collision_fn;
    std::function<void(int)> on_key_press_fn;
    std::function<void()> on_render_3d_fn;
    std::function<void(int, int)> on_render_hud_fn;

    int entity_id_counter = 1;

    int spawn_entity(const std::string& tag, MeshType type, vec3 pos, Material mat, float radius = 1.0f) {
        Entity e;
        e.id = entity_id_counter++;
        e.tag = tag;
        e.mesh_type = type;
        e.tr.position = pos;
        e.mat = mat;
        e.bounding_radius = radius;
        entities.push_back(e);
        return e.id;
    }

    Entity* get_entity(int id) {
        for (auto& e : entities) {
            if (e.id == id && e.is_alive) return &e;
        }
        return nullptr;
    }

    void play_sound_fx(int type) {
        if (type == 1) { // Laser shot
            Beep(1200, 30);
        } else if (type == 2) { // Explosion
            Beep(350, 70);
        } else if (type == 3) { // Player hurt
            Beep(240, 90);
        }
    }

    bool is_fullscreen = false;
    RECT windowed_rect = { 100, 100, 1380, 820 };

    void toggle_fullscreen() {
        if (!hwnd) return;
        is_fullscreen = !is_fullscreen;
        if (is_fullscreen) {
            GetWindowRect(hwnd, &windowed_rect);
            int sw = GetSystemMetrics(SM_CXSCREEN);
            int sh = GetSystemMetrics(SM_CYSCREEN);
            SetWindowLong(hwnd, GWL_STYLE, WS_POPUP | WS_VISIBLE);
            SetWindowPos(hwnd, HWND_TOP, 0, 0, sw, sh, SWP_FRAMECHANGED | SWP_SHOWWINDOW);
            width = sw;
            height = sh;
        } else {
            SetWindowLong(hwnd, GWL_STYLE, WS_OVERLAPPEDWINDOW | WS_VISIBLE);
            SetWindowPos(hwnd, HWND_TOP, windowed_rect.left, windowed_rect.top,
                         windowed_rect.right - windowed_rect.left,
                         windowed_rect.bottom - windowed_rect.top,
                         SWP_FRAMECHANGED | SWP_SHOWWINDOW);
            width = windowed_rect.right - windowed_rect.left;
            height = windowed_rect.bottom - windowed_rect.top;
        }
        glViewport(0, 0, width, height);
    }

    void init_window(const char* title, int w, int h, bool start_fullscreen = false) {
        WNDCLASS wc = {};
        wc.lpfnWndProc = WndProcStatic;
        wc.hInstance = GetModuleHandle(nullptr);
        wc.lpszClassName = "Vortex3D_Engine_Class";
        wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
        RegisterClass(&wc);

        if (start_fullscreen) {
            width = GetSystemMetrics(SM_CXSCREEN);
            height = GetSystemMetrics(SM_CYSCREEN);
            is_fullscreen = true;
            hwnd = CreateWindowEx(
                WS_EX_APPWINDOW, wc.lpszClassName, title,
                WS_POPUP | WS_VISIBLE,
                0, 0, width, height,
                nullptr, nullptr, wc.hInstance, this
            );
        } else {
            width = w;
            height = h;
            is_fullscreen = false;
            hwnd = CreateWindowEx(
                0, wc.lpszClassName, title,
                WS_OVERLAPPEDWINDOW | WS_VISIBLE,
                CW_USEDEFAULT, CW_USEDEFAULT, width, height,
                nullptr, nullptr, wc.hInstance, this
            );
        }

        hdc = GetDC(hwnd);

        PIXELFORMATDESCRIPTOR pfd = {};
        pfd.nSize = sizeof(pfd);
        pfd.nVersion = 1;
        pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER;
        pfd.iPixelType = PFD_TYPE_RGBA;
        pfd.cColorBits = 32;
        pfd.cDepthBits = 24;

        int pf = ChoosePixelFormat(hdc, &pfd);
        SetPixelFormat(hdc, pf, &pfd);
        hglrc = wglCreateContext(hdc);
        wglMakeCurrent(hdc, hglrc);

        init_opengl();
    }

    void init_opengl() {
        glEnable(GL_DEPTH_TEST);
        glDepthFunc(GL_LEQUAL);
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);
        glEnable(GL_COLOR_MATERIAL);
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE);

        if (fog_enabled) {
            glEnable(GL_FOG);
            GLfloat f_col[] = { fog_color.r, fog_color.g, fog_color.b, 1.0f };
            glFogfv(GL_FOG_COLOR, f_col);
            glFogi(GL_FOG_MODE, GL_EXP2);
            glFogf(GL_FOG_DENSITY, 0.015f);
        }

        sun.position = vec3(20, 40, 20);
        GLfloat light_pos[] = { sun.position.x, sun.position.y, sun.position.z, 1.0f };
        GLfloat light_diff[] = { 1.0f, 0.95f, 0.9f, 1.0f };
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos);
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diff);

        GLfloat amb[] = { ambient_light.r, ambient_light.g, ambient_light.b, 1.0f };
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, amb);
    }

    void run() {
        if (on_start_fn) on_start_fn();

        auto prev_time = std::chrono::high_resolution_clock::now();
        MSG msg = {};

        while (running) {
            while (PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE)) {
                if (msg.message == WM_QUIT) {
                    running = false;
                }
                TranslateMessage(&msg);
                DispatchMessage(&msg);
            }

            auto curr_time = std::chrono::high_resolution_clock::now();
            float dt = std::chrono::duration<float>(curr_time - prev_time).count();
            if (dt < 1.0f / fps_cap) {
                float sleep_sec = (1.0f / fps_cap) - dt;
                Sleep((DWORD)(sleep_sec * 1000.0f));
                curr_time = std::chrono::high_resolution_clock::now();
                dt = std::chrono::duration<float>(curr_time - prev_time).count();
            }
            prev_time = curr_time;
            if (dt > 0.1f) dt = 0.1f; // Clamp delta spike

            update_game(dt);
            render_frame();
        }

        cleanup();
    }

    void update_game(float dt) {
        // Physics and velocity updates
        for (auto& e : entities) {
            if (!e.is_alive) continue;

            if (e.use_gravity) {
                e.velocity.y -= 25.0f * dt;
            }

            e.tr.position += e.velocity * dt;

            // Ground plane collision (Y = 0)
            if (e.tr.position.y <= e.bounding_radius && e.use_gravity) {
                e.tr.position.y = e.bounding_radius;
                e.velocity.y = 0;
                e.is_grounded = true;
            }
        }

        // Collision detection pairs
        for (size_t i = 0; i < entities.size(); ++i) {
            if (!entities[i].is_alive) continue;
            for (size_t j = i + 1; j < entities.size(); ++j) {
                if (!entities[j].is_alive) continue;

                float dist = vec3::distance(entities[i].tr.position, entities[j].tr.position);
                float rad_sum = entities[i].bounding_radius + entities[j].bounding_radius;
                if (dist < rad_sum) {
                    if (on_collision_fn) {
                        on_collision_fn(entities[i], entities[j]);
                    }
                }
            }
        }

        particles.update(dt);

        if (on_update_fn) {
            on_update_fn(dt);
        }

        // Reset mouse deltas
        mouse_dx = 0;
        mouse_dy = 0;
        std::copy(std::begin(keys), std::end(keys), std::begin(keys_prev));
        mouse_left_prev = mouse_left;
    }

    void render_frame() {
        glClearColor(fog_color.r, fog_color.g, fog_color.b, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // Setup 3D Camera Projection
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        float aspect = (float)width / (float)height;
        float fov = main_camera.fov * (3.14159265f / 180.0f);
        float h = std::tan(fov * 0.5f) * main_camera.near_z;
        float w = h * aspect;
        glFrustum(-w, w, -h, h, main_camera.near_z, main_camera.far_z);

        // Setup View Matrix
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();

        // Rotate & Translate Camera
        glRotatef(main_camera.pitch, 1, 0, 0);
        glRotatef(main_camera.yaw, 0, 1, 0);
        glTranslatef(-main_camera.position.x, -main_camera.position.y, -main_camera.position.z);

        if (on_render_3d_fn) {
            on_render_3d_fn();
        } else {
            // Draw Arena Grid / Cyberpunk Terrain
            draw_cyber_grid(80.0f, 40);

            // Draw Entities
            for (const auto& e : entities) {
                if (!e.is_alive) continue;

                glPushMatrix();
                glTranslatef(e.tr.position.x, e.tr.position.y, e.tr.position.z);
                glRotatef(e.tr.rotation.y, 0, 1, 0);
                glRotatef(e.tr.rotation.x, 1, 0, 0);
                glRotatef(e.tr.rotation.z, 0, 0, 1);
                glScalef(e.tr.scale.x, e.tr.scale.y, e.tr.scale.z);

                glColor4f(e.mat.albedo.r, e.mat.albedo.g, e.mat.albedo.b, e.mat.albedo.a);

                if (e.mesh_type == MeshType::CUBE) {
                    draw_cube(1.0f);
                } else if (e.mesh_type == MeshType::LASER) {
                    draw_laser_bolt();
                } else if (e.mesh_type == MeshType::PILLAR) {
                    draw_pillar();
                } else {
                    draw_cube(1.0f);
                }

                glPopMatrix();
            }
        }

        // Draw particles
        particles.render();

        // Draw 2D HUD overlay
        if (on_render_hud_fn) {
            on_render_hud_fn(width, height);
        } else {
            hud.draw(width, height);
        }

        SwapBuffers(hdc);
    }

    void draw_cube(float s) {
        float h = s * 0.5f;
        glBegin(GL_QUADS);
        // Front
        glNormal3f(0, 0, 1);
        glVertex3f(-h, -h,  h); glVertex3f( h, -h,  h); glVertex3f( h,  h,  h); glVertex3f(-h,  h,  h);
        // Back
        glNormal3f(0, 0, -1);
        glVertex3f(-h, -h, -h); glVertex3f(-h,  h, -h); glVertex3f( h,  h, -h); glVertex3f( h, -h, -h);
        // Top
        glNormal3f(0, 1, 0);
        glVertex3f(-h,  h, -h); glVertex3f(-h,  h,  h); glVertex3f( h,  h,  h); glVertex3f( h,  h, -h);
        // Bottom
        glNormal3f(0, -1, 0);
        glVertex3f(-h, -h, -h); glVertex3f( h, -h, -h); glVertex3f( h, -h,  h); glVertex3f(-h, -h,  h);
        // Right
        glNormal3f(1, 0, 0);
        glVertex3f( h, -h, -h); glVertex3f( h,  h, -h); glVertex3f( h,  h,  h); glVertex3f( h, -h,  h);
        // Left
        glNormal3f(-1, 0, 0);
        glVertex3f(-h, -h, -h); glVertex3f(-h, -h,  h); glVertex3f(-h,  h,  h); glVertex3f(-h,  h, -h);
        glEnd();
    }

    void draw_laser_bolt() {
        glDisable(GL_LIGHTING);
        glLineWidth(4.0f);
        glColor3f(0.0f, 1.0f, 0.9f);
        glBegin(GL_LINES);
        glVertex3f(0, 0, -1.2f);
        glVertex3f(0, 0,  1.2f);
        glEnd();
        glEnable(GL_LIGHTING);
    }

    void draw_pillar() {
        float h = 6.0f;
        float w = 1.0f;
        glBegin(GL_QUADS);
        glNormal3f(0, 0, 1);
        glVertex3f(-w, 0, w); glVertex3f(w, 0, w); glVertex3f(w, h, w); glVertex3f(-w, h, w);
        glNormal3f(0, 0, -1);
        glVertex3f(-w, 0, -w); glVertex3f(-w, h, -w); glVertex3f(w, h, -w); glVertex3f(w, 0, -w);
        glNormal3f(1, 0, 0);
        glVertex3f(w, 0, -w); glVertex3f(w, h, -w); glVertex3f(w, h, w); glVertex3f(w, 0, w);
        glNormal3f(-1, 0, 0);
        glVertex3f(-w, 0, -w); glVertex3f(-w, 0, w); glVertex3f(-w, h, w); glVertex3f(-w, h, -w);
        glEnd();
    }

    void draw_cyber_grid(float size, int divisions) {
        glDisable(GL_LIGHTING);
        float step = size / divisions;
        float half = size * 0.5f;

        glLineWidth(1.0f);
        glColor4f(0.0f, 0.45f, 0.65f, 0.4f);
        glBegin(GL_LINES);
        for (int i = 0; i <= divisions; ++i) {
            float coord = -half + i * step;
            glVertex3f(coord, 0.0f, -half);
            glVertex3f(coord, 0.0f,  half);
            glVertex3f(-half, 0.0f, coord);
            glVertex3f( half, 0.0f, coord);
        }
        glEnd();

        // Dark floor polygon underneath
        glColor3f(0.04f, 0.05f, 0.08f);
        glBegin(GL_QUADS);
        glVertex3f(-half, -0.05f, -half);
        glVertex3f( half, -0.05f, -half);
        glVertex3f( half, -0.05f,  half);
        glVertex3f(-half, -0.05f,  half);
        glEnd();

        glEnable(GL_LIGHTING);
    }

    void cleanup() {
        wglMakeCurrent(nullptr, nullptr);
        if (hglrc) wglDeleteContext(hglrc);
        if (hdc && hwnd) ReleaseDC(hwnd, hdc);
        if (hwnd) DestroyWindow(hwnd);
    }

    static LRESULT CALLBACK WndProcStatic(HWND wnd, UINT msg, WPARAM wp, LPARAM lp) {
        Engine* eng = &instance();
        switch (msg) {
            case WM_CLOSE:
                eng->running = false;
                return 0;
            case WM_SIZE:
                eng->width = LOWORD(lp);
                eng->height = HIWORD(lp);
                glViewport(0, 0, eng->width, eng->height);
                return 0;
            case WM_KEYDOWN:
                if (wp == VK_F11) {
                    eng->toggle_fullscreen();
                    return 0;
                }
                if (wp < 256) eng->keys[wp] = true;
                if (eng->on_key_press_fn) eng->on_key_press_fn((int)wp);
                return 0;
            case WM_KEYUP:
                if (wp < 256) eng->keys[wp] = false;
                return 0;
            case WM_LBUTTONDOWN:
                eng->mouse_left = true;
                return 0;
            case WM_LBUTTONUP:
                eng->mouse_left = false;
                return 0;
            case WM_RBUTTONDOWN:
                eng->keys[VK_RBUTTON] = true;
                return 0;
            case WM_RBUTTONUP:
                eng->keys[VK_RBUTTON] = false;
                return 0;
            case WM_MOUSEWHEEL: {
                short delta = GET_WHEEL_DELTA_WPARAM(wp);
                if (delta > 0 && eng->on_key_press_fn) eng->on_key_press_fn(1001); // Wheel Up
                if (delta < 0 && eng->on_key_press_fn) eng->on_key_press_fn(1002); // Wheel Down
                return 0;
            }
            case WM_MOUSEMOVE: {
                int new_x = LOWORD(lp);
                int new_y = HIWORD(lp);
                eng->mouse_dx = new_x - eng->mouse_x;
                eng->mouse_dy = new_y - eng->mouse_y;
                eng->mouse_x = new_x;
                eng->mouse_y = new_y;
                return 0;
            }
        }
        return DefWindowProc(wnd, msg, wp, lp);
    }
};

} // namespace vortex

#endif // VORTEX_ENGINE_HPP
