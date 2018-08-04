/* 
 * Pass in the joint angles and get back the foot position relative to 
 * the leg mount point
 */
void forward_kinematics(
        float shoulder_radians, float elbow_radians, float wrist_radians, 
        float* x_pos, float* y_pos, float* z_pos);


/* 
 * Pass in a Vec3 target position, and get back a tuple of joint angles.
 * Position is relative to the legs mounting point. The variable flip is used
 * to indicate which solution to use. It should be either +1.0 or -1.0
 */
void inverse_kinematics(
    float x_pos, float y_pos, float z_pos, float flip,
    float* shoulder_radians, float* elbow_radians, float* wrist_radians);
