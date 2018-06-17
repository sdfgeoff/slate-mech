from .gun import Gun


class Robot:
    def __init__(self, telemetry, controller, hardware):
        self.telemetry = telemetry
        self.controller = controller
        self.hardware = hardware

        self.gun = Gun(self.telemetry, self.hardware)

        # Allow the gun to not fire when a controller connects
        self.controller.on_controller_connected.append(
            self._on_controller_connected
        )


    def update(self):
        self.telemetry.update()
        self.controller.update()

        self.gun.set_id(self.controller.get_bullet_id())
        self.gun.active = self.controller.get_weapon_active()
        self.gun.update()

    def _on_controller_connected(self):
        self.gun.sync(
            self.controller.get_bullet_id()
        )



