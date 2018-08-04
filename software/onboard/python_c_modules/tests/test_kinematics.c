#include "kinematics/kinematics.h"
#include "unity.h"

#define PRECISION 1e-4

void test_fk(void){
    float x, y, z;
    forward_kinematics(0.0, 0.0, 0.0, &x, &y, &z);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.15, x);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, y);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, z);
    
    forward_kinematics(0.0, 0.0, M_PI/2, &x, &y, &z);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.10, x);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, y);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, -0.05, z);
    
    forward_kinematics(0.0, M_PI/2, 0.0, &x, &y, &z);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.05, x);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.1, y);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, z);
    
    forward_kinematics(0.0, -M_PI/2, 0.0, &x, &y, &z);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.05, x);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, -0.1, y);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, z);
    
    forward_kinematics(0.0, -M_PI/2, 0.0, &x, &y, &z);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.05, x);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, -0.1, y);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, z);
    
    forward_kinematics(-M_PI/2, 0.0, 0.0, &x, &y, &z);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, x);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, -0.15, y);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, z);
    
    forward_kinematics(-M_PI/2, M_PI/2, 0.0, &x, &y, &z);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.1, x);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, -0.05, y);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, z);
}

void test_ik(void) {
    float shoulder, elbow, wrist;
    inverse_kinematics(0.15, 0.0, 0.0, -1.0, &shoulder, &elbow, &wrist);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, shoulder);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, elbow);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, wrist);
    
    inverse_kinematics(0.10, 0.0, -0.05, 1.0, &shoulder, &elbow, &wrist);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, shoulder);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, elbow);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, M_PI/2, wrist);
    
    inverse_kinematics(0.05, 0.1, 0.0, 1.0, &shoulder, &elbow, &wrist);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, shoulder);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, M_PI/2, elbow);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, wrist);
    
    inverse_kinematics(0.05, -0.1, 0.0, -1.0, &shoulder, &elbow, &wrist);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, shoulder);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, -M_PI/2, elbow);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, 0.0, wrist);
    
    // Check that we can get both solutions with the flip parameter
    inverse_kinematics(0.1 / pow(2.0, 0.5), 0.0, -0.05, -1.0, &shoulder, &elbow, &wrist);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, M_PI/4, shoulder);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, -M_PI/2, elbow);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, M_PI/2, wrist);
    
    inverse_kinematics(0.1 / pow(2.0, 0.5), 0.0, -0.05, 1.0, &shoulder, &elbow, &wrist);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, -M_PI/4, shoulder);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, M_PI/2, elbow);
    TEST_ASSERT_FLOAT_WITHIN(PRECISION, M_PI/2, wrist);
}

void test_kinematics(void){
    RUN_TEST(test_fk);
    RUN_TEST(test_ik);
}
