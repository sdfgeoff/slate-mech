class Gun:
    """Handles bullet_id's to ensure projectiles don't shoot accidentally"""
    def __init__(self, telemetry, hardware):
        self.telemetry = telemetry
        self.hardware = hardware

        self.last_bullet_id = 0
        self.new_bullet_id = 0


        self.active = False
        self._active = True
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
        if self._active != self.active:
            self.sync(self.new_bullet_id)
            self._active = self.active
            self._check_shoot()

            self.telemetry.log(
                self.telemetry.INFO,
                "Weapons Systems Online" if self.active else "Weapons Systems Offline"
            )
            self.telemetry.var_val(
                "gun_online",
                self.active,
                self.telemetry.INFO if self.active else self.telemetry.WARN
            )

        if self.active:
            self.hardware.set_digital(self.hardware.GUN_WARNING_LIGHT, 1)
            self._check_shoot()
        else:
            self.hardware.set_digital(self.hardware.GUN_WARNING_LIGHT, 0)
            self.hardware.set_digital(self.hardware.GUN_TRIGGER, 0)


    def _check_shoot(self):
        if self.new_bullet_id != self.last_bullet_id:
            # Set early so if something goes wrong, we don't continue
            # firing
            self.last_bullet_id = self.new_bullet_id

            # Fire the gun
            self.hardware.set_digital(self.hardware.GUN_TRIGGER, 1)

            self.telemetry.var_val(
                "bullet_id",
                self.new_bullet_id,
                self.telemetry.INFO,
            )
        else:
            self.hardware.set_digital(self.hardware.GUN_TRIGGER, 0)
