import taichi as ti
from simulator import Simulator
import time
import math


@ti.data_oriented
class SimulationGUI(object):
    def __init__(self, sim: Simulator, title: str = "Simulator", resolution=(800, 600)) -> None:
        super().__init__()

        self.sim = sim

        self.bound_min = ti.Vector([0.0,0.0,0.0], dt=ti.f32)
        self.bound_max = self.sim.grid_extent
        self.bound_extent = self.bound_max - self.bound_min
        self.bound_center = 0.5 * self.bound_extent + self.bound_min
        # Particle visualization radius
        self.p_radius = self.sim.cell_extent * 0.5

        self.resolution = resolution
        self.window = ti.ui.Window(title, resolution, vsync=True)
        self.canvas = self.window.get_canvas()
        self.scene = ti.ui.Scene()
        self.camera = ti.ui.make_camera()
        self.reset_camera()

        self.reset()


    def reset(self):
        self.t_sim = 0.0
        self.t_render = 0.0
        self.export_mesh = False

    def reset_camera(self):
        # Offset the camera position from the center of the bound along -Y
        self.camera.position(self.bound_center.x, self.bound_center.y - self.bound_extent.y, self.bound_center.z)
        self.camera.lookat(self.bound_center.x, self.bound_center.y, self.bound_center.z)
        self.camera.up(0.0, 0.0, 1.0)
        self.camera.fov(math.degrees(math.atan2(self.bound_extent.y, self.bound_extent.x)*2.0))  # todo: compute this
        # self.camera.projection_mode()
        self.scene.set_camera(self.camera)

    # def draw_center(self):
    #     center

    def render(self):

        # This seems to be a bug... If no point light exists then interal error would occur
        self.scene.point_light(pos=tuple(self.bound_center), color=(5, 5, 5))
        # Use the ambient light to see the particles
        self.scene.ambient_light((1, 1, 1))
        # Draw the particles
        if not self.sim.simulate_sand:
            self.scene.particles(self.sim.particles_position, radius=0.25*self.p_radius, color=(0.0,0.0,1.0))
        else:
            self.scene.particles(self.sim.particles_position, radius=0.25 * self.p_radius, color=(1.0, 1.0, 0.0))

        self.canvas.scene(self.scene)
        self.window.show()

    def run(self):
        while self.window.running:

            # handle user input
            for e in self.window.get_events(tag='Press'):
                #if e.action == ti.ui.PRESS:
                    self.gui_event_callback(e)

            # Export the mesh if required
            if self.export_mesh:
                self.sim.reconstruct_mesh()


            # Simulation step
            self.sim.step()
            self.t_sim = self.sim.t

            # Render
            while self.t_render < self.t_sim:   # In the case that simulation step is large
                t_render_beg = time.time()
                # update gui
                self.render()
                t_render_end = time.time()
                self.t_render += t_render_end - t_render_beg

    def gui_event_callback(self, event):

        if event.key == "Space":    # Export mesh only for one frame
            if not self.export_mesh:
                self.sim.reconstruct_mesh()
        elif event.key == "m":   # Toggle the flag to export mesh continuously
            self.export_mesh = not self.export_mesh



