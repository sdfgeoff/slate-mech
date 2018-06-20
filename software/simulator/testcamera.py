import mathutils
import bge
SPEED = 0.2


def activate_testcam(cont):
    cont.owner.scene.active_camera = cont.owner
    cont.owner.scene.objects['VidTx']['enable'] = False
    cont.owner.scene.objects['CamDistort']['enable'] = False

    bge.constraints.setDebugMode((
        bge.constraints.DBG_DRAWCONTACTPOINTS +
        bge.constraints.DBG_DRAWCONSTRAINTLIMITS +
        bge.constraints.DBG_DRAWCONSTRAINTS
    ))

    for obj in cont.owner.scene.objects:
        if "PHYS_DEBUG" in obj:
            print("HERE")
            obj.visible = True


def deactivate_testcam(cont):
    cont.owner.scene.objects['VidTx']['enable'] = True
    cont.owner.scene.objects['CamDistort']['enable'] = True
    cont.owner.scene.active_camera = cont.owner.scene.objects['RobotCamera']

    bge.constraints.setDebugMode(bge.constraints.DBG_NODEBUG)
    for obj in cont.owner.scene.objects:
        if "PHYS_DEBUG" in obj:
            obj.visible = False


def run(cont):
    if "init" not in cont.owner:
        deactivate_testcam(cont)
        cont.owner["init"] = True


    if bge.logic.keyboard.events[bge.events.TABKEY] == 1:
        cont.owner["active"] = not cont.owner["active"]
        if cont.owner["active"]:
            activate_testcam(cont)
        else:
            deactivate_testcam(cont)

    if cont.owner["active"]:
        cont.activate(cont.actuators["Mouse"])

        lin = mathutils.Vector()
        if bge.logic.keyboard.events[bge.events.RKEY]:
            lin.y += SPEED
        if bge.logic.keyboard.events[bge.events.FKEY]:
            lin.y -= SPEED
        if bge.logic.keyboard.events[bge.events.AKEY]:
            lin.x -= SPEED
        if bge.logic.keyboard.events[bge.events.DKEY]:
            lin.x += SPEED
        if bge.logic.keyboard.events[bge.events.SKEY]:
            lin.z += SPEED
        if bge.logic.keyboard.events[bge.events.WKEY]:
            lin.z -= SPEED


        cont.owner.worldPosition += cont.owner.worldOrientation * lin
