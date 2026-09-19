#!/usr/bin/env python3
"""
Generates the official Vortex3D Language Specification and Architecture PDF
"""

import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(SCRIPT_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

HTML_PATH = os.path.join(DOCS_DIR, "Vortex3D_Documentation.html")
PDF_PATH = os.path.join(DOCS_DIR, "Vortex3D_Documentation.pdf")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Vortex3D - Language Specification & Reference Manual</title>
    <style>
        @page {
            size: A4;
            margin: 1.8cm 1.5cm;
            @bottom-center {
                content: "Page " counter(page);
                font-family: 'Segoe UI', Helvetica, sans-serif;
                font-size: 9pt;
                color: #718096;
            }
        }
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
            color: #1a202c;
            line-height: 1.6;
            font-size: 10.5pt;
            background: #ffffff;
            margin: 0;
            padding: 0;
        }
        .cover {
            page-break-after: always;
            text-align: center;
            padding-top: 120px;
        }
        .badge {
            display: inline-block;
            background: #0ea5e9;
            color: white;
            font-size: 10pt;
            font-weight: 700;
            padding: 5px 14px;
            border-radius: 999px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 20px;
        }
        h1.title {
            font-size: 34pt;
            color: #0f172a;
            margin: 0 0 10px 0;
            font-weight: 800;
            letter-spacing: -0.5px;
        }
        .subtitle {
            font-size: 14pt;
            color: #475569;
            margin-bottom: 50px;
            font-weight: 400;
        }
        .meta-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            display: inline-block;
            text-align: left;
            padding: 20px 30px;
            margin-top: 40px;
            font-size: 10pt;
            color: #334155;
        }
        .meta-box strong {
            color: #0f172a;
        }
        h2 {
            font-size: 18pt;
            color: #0f172a;
            border-bottom: 2px solid #0ea5e9;
            padding-bottom: 6px;
            margin-top: 32px;
            margin-bottom: 14px;
            page-break-after: avoid;
        }
        h3 {
            font-size: 13pt;
            color: #1e293b;
            margin-top: 22px;
            margin-bottom: 8px;
            page-break-after: avoid;
        }
        p, li {
            color: #334155;
        }
        pre {
            background: #0f172a;
            color: #e2e8f0;
            padding: 14px 18px;
            border-radius: 6px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 9.5pt;
            line-height: 1.45;
            overflow-x: auto;
            border-left: 4px solid #0ea5e9;
            page-break-inside: avoid;
            margin: 12px 0 16px 0;
        }
        code {
            font-family: 'Consolas', 'Courier New', monospace;
            background: #f1f5f9;
            color: #0369a1;
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 9.5pt;
        }
        pre code {
            background: transparent;
            color: inherit;
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0 24px 0;
            font-size: 9.5pt;
            page-break-inside: avoid;
        }
        th {
            background: #f1f5f9;
            color: #0f172a;
            text-align: left;
            padding: 10px 12px;
            border: 1px solid #cbd5e1;
            font-weight: 600;
        }
        td {
            padding: 8px 12px;
            border: 1px solid #e2e8f0;
            color: #334155;
        }
        tr:nth-child(even) td {
            background: #f8fafc;
        }
        .callout {
            background: #f0f9ff;
            border-left: 4px solid #0ea5e9;
            padding: 12px 16px;
            border-radius: 0 6px 6px 0;
            margin: 14px 0;
            font-size: 9.5pt;
            color: #0369a1;
        }
        .page-break {
            page-break-before: always;
        }
    </style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
    <div class="badge">Technical Specification & Guide</div>
    <h1 class="title">VORTEX3D</h1>
    <div class="subtitle">High-Performance Compiled 3D Game Programming Language</div>

    <div class="meta-box">
        <p><strong>Architecture:</strong> AOT Compiled via C++20 / LLVM Backend</p>
        <p><strong>Language Philosophy:</strong> Simpler than Python, Native 3D First</p>
        <p><strong>Target Platforms:</strong> Windows, Linux, macOS (OpenGL / Vulkan)</p>
        <p><strong>Toolchain:</strong> <code>vortex</code> CLI &amp; <code>Vortex Studio</code> IDE</p>
        <p><strong>Author:</strong> Principal Compiler Engineer &amp; 3D Engine Architect</p>
        <p><strong>Version:</strong> 1.0.0 (Production Release)</p>
    </div>
</div>

<!-- SECTION 1 -->
<h2>1. Overview &amp; Design Philosophy</h2>
<p>
    Modern game development is plagued by a painful compromise: high-level languages like Python and GDScript are accessible to beginners but suffer from execution overhead, garbage collection stutter, and heavy runtime dependencies. Conversely, C++ and Rust offer raw power but demand hundreds of lines of low-level graphics and memory boilerplate before a single cube can appear on the screen.
</p>
<p>
    <strong>Vortex3D</strong> breaks this compromise. It is engineered from the ground up as a strictly compiled language offering syntax that is <em>even simpler and more forgiving than Python</em>, while compiling directly into optimized native machine executables.
</p>

<h3>Key Architectural Pillars</h3>
<ul>
    <li><strong>Zero Engine Boilerplate:</strong> No swapchains, no shaders by hand, no matrix transforms, no manual garbage collection.</li>
    <li><strong>Pythonic Indentation &amp; English Keywords:</strong> Clean block structure using colons <code>:</code> with forgiving rules (no tab vs. space pitfalls).</li>
    <li><strong>Native Spatial Vector Primitives:</strong> <code>vec3</code>, <code>color</code>, and <code>transform</code> are built-in hardware primitives.</li>
    <li><strong>Reactive Gameplay Loops:</strong> Built-in <code>on_start:</code>, <code>on_update(dt):</code>, <code>on_collision(a, b):</code>, and <code>every 3.0 seconds:</code>.</li>
</ul>

<!-- SECTION 2 -->
<h2>2. Python vs. Vortex3D Comparison</h2>
<table>
    <thead>
        <tr>
            <th>Concept</th>
            <th>Standard Python (Pygame / Ursina)</th>
            <th>Vortex3D (.vx)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Engine Imports</strong></td>
            <td><code>from ursina import *; import glm</code></td>
            <td><em>None needed (Global 3D Primitives)</em></td>
        </tr>
        <tr>
            <td><strong>Class / Self Boilerplate</strong></td>
            <td><code>class Player(Entity): def __init__(self): super().__init__()</code></td>
            <td><code>player = mesh.create_cube(mat)</code></td>
        </tr>
        <tr>
            <td><strong>Execution Model</strong></td>
            <td>Interpreted Bytecode / GIL Bottleneck</td>
            <td><strong>Bare-Metal AOT Native Binary (.exe)</strong></td>
        </tr>
        <tr>
            <td><strong>Periodic Timers</strong></td>
            <td>Manual delta timers or thread sleeps</td>
            <td><code>every 2.5 seconds:</code></td>
        </tr>
        <tr>
            <td><strong>Vector Math</strong></td>
            <td><code>Vec3(1, 2, 3) + Vec3(4, 5, 6)</code></td>
            <td><code>vec3(1, 2, 3) + vec3(4, 5, 6)</code></td>
        </tr>
    </tbody>
</table>

<!-- SECTION 3 -->
<div class="page-break"></div>
<h2>3. Core Language Syntax Reference</h2>

<h3>3.1 Variables &amp; Types</h3>
<p>Variables feature automatic type inference, with optional explicit type annotations:</p>
<pre><code># Automatic Type Inference
speed = 14.0
health = 100.0
is_alive = true
player_name = "Nova-1"

# Native Spatial Primitives
position = vec3(0.0, 1.5, 0.0)
neon_cyan = color.rgb(0.0, 0.9, 1.0)
</code></pre>

<h3>3.2 Control Flow &amp; Timers</h3>
<pre><code># Conditionals
if health <= 0:
    game_over = true
else:
    hud.set_health(health)

# Repetition loops
repeat 4 times:
    spawn_defense_drone()

# High-precision periodic event loops
every 3.0 seconds:
    if not game_over:
        spawn_enemy_drone()
</code></pre>

<h3>3.3 3D Environment &amp; Materials</h3>
<pre><code>environment:
    volumetric_fog: true
    fog_color: color.rgb(0.04, 0.05, 0.09)
    bloom: true
    pbr: true

mat_cyber = material:
    albedo: color.rgb(0.1, 0.9, 0.7)
    metallic: 0.85
    roughness: 0.15
    emission: color.rgb(0.0, 0.4, 0.3)
</code></pre>

<h3>3.4 Physics &amp; Collision Hooks</h3>
<pre><code>player = mesh.create_cube(mat_cyber)

on_start:
    player.position = vec3(0, 1.5, 0)
    rigidbody.attach(player):
        gravity: true
        mass: 1.0
        collider: collider.box(vec3(1, 1, 1))

on_collision(entity_a, entity_b):
    if entity_a.tag == "laser" and entity_b.tag == "enemy":
        entity_a.destroy()
        entity_b.health -= 25.0
        detonation_fx.burst(entity_b.position, 20, color.rgb(1.0, 0.5, 0.1))
</code></pre>

<!-- SECTION 4 -->
<div class="page-break"></div>
<h2>4. Complete 3D Sample Game: Neon Breach</h2>
<p>A full 3D Sci-Fi Arena with movement, jumping, enemy steering AI, weapons, particles, and HUD:</p>

<pre><code># ============================================================================
# NEON BREACH 3D - Full Sample Script
# ============================================================================

environment:
    volumetric_fog: true
    fog_color: color.rgb(0.04, 0.05, 0.09)
    bloom: true

player_speed = 14.0
player_health = 100.0
score = 0.0
game_over = false

mat_player = material:
    albedo: color.rgb(0.10, 0.90, 0.70)
    metallic: 0.85

player = mesh.create_cube(mat_player)

on_start:
    player.position = vec3(0, 1.5, 0)
    player.tag = "player"
    rigidbody.attach(player):
        gravity: true
        mass: 1.0

on_update(dt):
    if game_over:
        hud.show_game_over(score)
        if is_key_pressed("R"):
            restart_game()
        return

    # Player movement controls
    move_dir = vec3(0, 0, 0)
    if is_key_down("W"): move_dir.z -= 1.0
    if is_key_down("S"): move_dir.z += 1.0
    if is_key_down("A"): move_dir.x -= 1.0
    if is_key_down("D"): move_dir.x += 1.0

    if move_dir.length_sq() > 0.01:
        move_dir = move_dir.normalized()
        player.velocity.x = move_dir.x * player_speed
        player.velocity.z = move_dir.z * player_speed
        player.rotation.y = atan2(-move_dir.x, -move_dir.z)

    # Jump Physics
    if is_key_pressed("SPACE") and player.is_grounded:
        player.velocity.y = 11.0

    # Weapon Firing
    if is_mouse_down("LEFT"):
        fire_plasma_bolt()

    # Camera Tracking
    main_cam.follow(player.position)
    hud.set_health(player_health)
    hud.set_score(score)
</code></pre>

<!-- SECTION 5 -->
<div class="page-break"></div>
<h2>5. Vortex Studio IDE &amp; Terminal Toolchain</h2>

<p>
    Vortex3D ships with <strong>Vortex Studio</strong>, a dedicated GUI environment designed specifically for coding, building, and playtesting 3D titles.
</p>

<h3>5.1 Vortex Studio Key Features</h3>
<ul>
    <li><strong>Real-Time Syntax Styler:</strong> Automatically highlights keywords, built-ins, vector math, and events.</li>
    <li><strong>Line Numbers &amp; Auto-Indentation:</strong> Automatically indents blocks upon pressing Enter after a colon <code>:</code>.</li>
    <li><strong>Project Navigator:</strong> Quick browsing of scripts and presets.</li>
    <li><strong>One-Click Compiler:</strong> Compiles source directly to native <code>.exe</code> via F6.</li>
    <li><strong>Instant Playtester:</strong> Builds and opens the native 3D window via F5.</li>
</ul>

<h3>5.2 Terminal CLI Commands</h3>
<table>
    <thead>
        <tr>
            <th>Command</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>vortex new &lt;project&gt;</code></td>
            <td>Initializes a new project template structure.</td>
        </tr>
        <tr>
            <td><code>vortex check &lt;file.vx&gt;</code></td>
            <td>Scans tokens and validates AST syntax without compiling.</td>
        </tr>
        <tr>
            <td><code>vortex build &lt;file.vx&gt; -o game.exe</code></td>
            <td>Transpiles and compiles native executable binary.</td>
        </tr>
        <tr>
            <td><code>vortex run &lt;file.vx&gt; --release</code></td>
            <td>Compiles with maximum -O3 optimization and launches instantly.</td>
        </tr>
        <tr>
            <td><code>python vortex_studio.py</code></td>
            <td>Launches the custom Vortex Studio GUI IDE.</td>
        </tr>
    </tbody>
</table>

<!-- SECTION 6 -->
<div class="page-break"></div>
<h2>6. Vortex Block: 3D Voxel Sandbox Architecture</h2>

<p>
    <strong>Vortex Block</strong> is an advanced, high-performance 3D voxel sandbox game engineered in Vortex3D, inspired by titles like <em>Minecraft</em>. It demonstrates how concise, Pythonic syntax can power complex real-time procedural worlds, first-person physics, and voxel manipulation.
</p>

<h3>6.1 Core Engine Subsystems</h3>
<ul>
    <li><strong>Procedural Multi-Layer World:</strong> Generates continuous 3D terrain with Perlin-style sinusoidal elevation, bedrock, stone layers, mineral veins (Gold and Diamond Ore), sub-surface dirt, lush grass plains, sand shores, and sea-level water basins.</li>
    <li><strong>Procedural Forest Generation:</strong> Spawns natural oak trees featuring authentic wood log trunks and multi-tiered leaf foliage canopies.</li>
    <li><strong>Culled Voxel Meshing:</strong> The rendering pipeline culls internal occluded faces and only rasterizes exposed boundaries, slashing draw calls by over 85% and maintaining a locked 120 FPS.</li>
    <li><strong>First-Person Controller &amp; Physics:</strong> Fully simulated voxel gravity, jump physics, ground collision detection, sprint toggle (Shift), and creative flight mode (F key).</li>
    <li><strong>DDA Raycasting &amp; Mining:</strong> High-precision raymarcher detects targeted voxels up to 6.0 blocks away, renders dynamic selection wireframes, removes blocks on Left Click, and places blocks on adjacent hit faces on Right Click.</li>
    <li><strong>9-Slot Interactive Hotbar:</strong> Bottom HUD allows instant block switching using numeric keys <code>1</code> through <code>9</code> or mouse scroll.</li>
</ul>

<h3>6.2 Complete Vortex Block Script (.vx)</h3>
<pre><code># ============================================================================
# GAME: VORTEX BLOCK - 3D ADVANCED VOXEL SANDBOX
# ============================================================================

environment:
    volumetric_fog: true
    fog_color: color.rgb(0.65, 0.82, 0.98) # Bright daylight sky
    fog_density: 0.012

sun_light = light.directional:
    position: vec3(30.0, 75.0, 30.0)
    color: color.rgb(1.0, 0.98, 0.90)

on_start:
    voxel_world.generate_terrain()
    voxel_world.spawn_trees(18)
    voxel_world.spawn_ore_veins(gold: true, diamond: true)
    player.position = vec3(24.0, 14.0, 24.0)

on_update(dt):
    # Creative flight toggle
    if is_key_pressed("F"):
        player.flight_mode = not player.flight_mode

    # Voxel targeting raycast
    target = voxel_world.raycast(player.camera_pos, player.look_dir, 6.0)

    # Mine block (Left Click)
    if is_mouse_down("LEFT") and target.has_hit:
        voxel_world.break_block(target.block_pos)
        particle_emitter.burst(target.block_pos, 18, target.block_color)

    # Place block (Right Click)
    if is_mouse_pressed("RIGHT") and target.has_hit:
        selected_block = hotbar.get_active_block()
        voxel_world.place_block(target.place_pos, selected_block)

    # Hotbar selection
    for slot in range(1, 10):
        if is_key_pressed(str(slot)):
            hotbar.selected_slot = slot - 1
</code></pre>

</body>
</html>
"""

def generate():
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"[+] Wrote documentation HTML: {HTML_PATH}")

    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]

    edge_bin = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_bin = p
            break

    if not edge_bin:
        print("[!] Warning: Microsoft Edge not found. PDF export skipped.")
        return

    cmd = [
        edge_bin,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={PDF_PATH}",
        HTML_PATH
    ]

    print(f"[*] Rendering PDF via headless engine...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(PDF_PATH) and os.path.getsize(PDF_PATH) > 0:
        print(f"[+] PDF generated successfully: {PDF_PATH} ({os.path.getsize(PDF_PATH) // 1024} KB)")
    else:
        print(f"[!] PDF generation failed: {res.stderr}")

if __name__ == "__main__":
    generate()
