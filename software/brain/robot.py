
class Robot:
    def __init__(self, telemetry, controller, hardware):
        self.telemetry = telemetry
        self.controller = controller
        self.hardware = hardware

        self.controller.on_controller_connected.append(
            self.on_controller_connected
        )

        self.gun = Gun(telemetry, hardware)
        self.i = 0

    def update(self):
        self.telemetry.update()
        self.controller.update()

        self.gun.set_id(self.controller.get_bullet_id())
        self.gun.update()

    def on_controller_connected(self):
        """Runs on the first packet when a controller connects to enable
        things to by synced"""
        self.gun.sync(
            self.controller.get_bullet_id()
        )


            # Need to sync these values on controller connect to prevent
            # accidental discharge

class Gun:
    """Handles bullet_id's to ensure projectiles don't shoot accidentally"""
    def __init__(self, telemetry, hardware):
        self.telemetry = telemetry
        self.telemetry.log(
            self.telemetry.DEBUG,
            "Weapons Systems Online"
        )
        self.last_bullet_id = 0
        self.new_bullet_id = 0
        self.hardware = hardware  # Function to call to fire the weapon

        self._shoot = False

    def sync(self, bullet_id):
        self.last_bullet_id = bullet_id
        self.new_bullet_id = bullet_id

        self.telemetry.log(
            self.telemetry.INFO,
            "Syncing bullet ID"
        )
        self.telemetry.var_val(
            "bullet_id",
            self.new_bullet_id,
            self.telemetry.INFO,
        )

    def set_id(self, bullet_id):
        self.new_bullet_id = bullet_id

    def update(self):
        if self.new_bullet_id != self.last_bullet_id:
            # Set early so if something goes wrong, we don't continue
            # firing
            self.last_bullet_id = self.new_bullet_id

            # Fire the gun
            self.hardware.set_digital(self.hardware.PIN_GUN, 1)

            self.telemetry.var_val(
                "bullet_id",
                self.new_bullet_id,
                self.telemetry.INFO,
            )
        else:
            self.hardware.set_digital(self.hardware.PIN_GUN, 0)



