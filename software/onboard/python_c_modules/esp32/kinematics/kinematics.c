#define SHOULDER_TO_ELBOW 0.05
#define ELBOW_TO_WRIST 0.05
#define WRIST_TO_TIP 0.05

#include <math.h>

static float clamp(float num) {
    /* Ensures that arcsin/arccos don't fail*/
    return fmax(fmin(num, 1.0), -1.0);
}

void forward_kinematics(
        float shoulder_radians, float elbow_radians, float wrist_radians, 
        float* x_pos, float* y_pos, float* z_pos) {
    elbow_radians = -elbow_radians;
    float extension = ELBOW_TO_WRIST + WRIST_TO_TIP*cos(-wrist_radians);
    *x_pos = SHOULDER_TO_ELBOW * cos(shoulder_radians) + extension * cos(shoulder_radians - elbow_radians);
    *y_pos = SHOULDER_TO_ELBOW * sin(shoulder_radians) + extension * sin(shoulder_radians - elbow_radians);
    *z_pos = -WRIST_TO_TIP * sin(wrist_radians);
}


void inverse_kinematics(
    float x_pos, float y_pos, float z_pos, float flip,
    float* shoulder_radians, float* elbow_radians, float* wrist_radians) {

    *wrist_radians = asin(clamp(-z_pos/WRIST_TO_TIP));
    float extension = ELBOW_TO_WRIST + WRIST_TO_TIP * cos(*wrist_radians);
    float dist = sqrt(pow(x_pos, 2.0) + pow(y_pos, 2.0));
    float b1 = atan2(y_pos, x_pos);
    
    float a1 = acos(clamp(  // cosine rule
        (pow(extension, 2.0) + pow(SHOULDER_TO_ELBOW, 2.0) - pow(dist, 2.0))
        / //-------------------------------------------------
        (2 * SHOULDER_TO_ELBOW * extension)));
    
    float a2 = acos(clamp(
        (pow(dist, 2.0) + pow(SHOULDER_TO_ELBOW, 2.0) - pow(extension, 2.0))
        /  //-------------------------------------------------
        (2 * SHOULDER_TO_ELBOW * dist)));
        
    *elbow_radians = flip * (M_PI - a1);
    *shoulder_radians = b1 - a2 * flip;
}
//~ def ik(pos, flipangles):
    //~ """Pass in a Vec3 target position, and get back a tuple of joint angles.
    //~ Position is relative to the legs mounting point"""
    //~ # TODO: Write unit tests
    //~ theta3 = -math.acos(clamp(-pos.z/L3))
    //~ extension = L2 + L3*math.sin(-theta3)
    //~ dist = math.sqrt(pos.x**2 + pos.y **2)
    //~ b1 = math.atan2(pos.y, pos.x)

    //~ a1 = math.acos(clamp((extension**2 + L1**2 - dist**2)/(2 * L1 * extension)))
    //~ a2 = math.acos(clamp((dist**2 + L1**2 - extension**2)/(2 * L1 * dist)))


    //~ theta2 = flipangles * (math.pi - a1)
    //~ theta1 = b1 - a2 * flipangles
    //~ return (theta1, theta2, theta3)



//~ def fk(theta1, theta2, theta3, flipangles):
    //~ """Pass in the joint angles and get back a Vec3 of the foot position
    //~ Position is relative to the legs mounting point"""
    //~ # TODO: Write unit tests
    //~ theta2 = -theta2
    //~ extension = L2 + L3*math.sin(-theta3)
    //~ y = L1 * math.sin(theta1) + extension * math.sin(theta1 - theta2)
    //~ x = L1 * math.cos(theta1) + extension * math.cos(theta1 - theta2)
    //~ z = -L3 * math.cos(theta3)
    //~ return geom.Vec3(x, y, z)
