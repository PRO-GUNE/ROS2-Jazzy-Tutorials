#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <sensor_msgs/msg/range.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <random>
#include <cmath>

class RobotController : public rclcpp::Node
{
public:
    RobotController() : Node("robot_controller")
    {
        // Publishers
        cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
        
        // Subscribers
        lidar_sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
            "sensor/lidar", 10, 
            std::bind(&RobotController::lidar_callback, this, std::placeholders::_1));
        
        sonar_sub_ = this->create_subscription<sensor_msgs::msg::Range>(
            "sensor/sonar", 10,
            std::bind(&RobotController::sonar_callback, this, std::placeholders::_1));
        
        camera_sub_ = this->create_subscription<sensor_msgs::msg::Image>(
            "sensor/camera/image_raw", 10,
            std::bind(&RobotController::camera_callback, this, std::placeholders::_1));
        
        // Timer for control loop
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&RobotController::control_loop, this));
        
        // Initialize random number generator
        rng_.seed(std::random_device{}());
        
        // Initialize state
        obstacle_detected_ = false;
        min_distance_ = 1.0;  // Minimum safe distance
        linear_speed_ = 0.3;  // Base linear speed
        angular_speed_ = 0.5; // Base angular speed
        
        RCLCPP_INFO(this->get_logger(), "Robot Controller Node Started");
    }

private:
    void lidar_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
    {
        // Process lidar data
        float min_range = std::numeric_limits<float>::max();
        int closest_index = -1;
        
        for (size_t i = 0; i < msg->ranges.size(); ++i) {
            if (msg->ranges[i] < min_range && msg->ranges[i] > msg->range_min) {
                min_range = msg->ranges[i];
                closest_index = i;
            }
        }
        
        lidar_min_distance_ = min_range;
        
        // Check if obstacle is detected
        if (min_range < min_distance_) {
            obstacle_detected_ = true;
            
            // Calculate angle to obstacle
            float angle_increment = msg->angle_increment;
            float angle_min = msg->angle_min;
            closest_obstacle_angle_ = angle_min + closest_index * angle_increment;
            
            RCLCPP_INFO(this->get_logger(), 
                "Obstacle detected at distance: %.2f, angle: %.2f", 
                min_range, closest_obstacle_angle_);
        } else {
            obstacle_detected_ = false;
        }
    }
    
    void sonar_callback(const sensor_msgs::msg::Range::SharedPtr msg)
    {
        sonar_range_ = msg->range;
        
        // Additional obstacle detection using sonar
        if (sonar_range_ < min_distance_) {
            obstacle_detected_ = true;
            RCLCPP_INFO(this->get_logger(), 
                "Sonar obstacle detected at distance: %.2f", sonar_range_);
        }
    }
    
    void camera_callback(const sensor_msgs::msg::Image::SharedPtr msg)
    {
        // For now, just log that camera data is received
        // You can implement computer vision processing here if needed
        static int count = 0;
        if (count++ % 50 == 0) {  // Log every 50th frame
            RCLCPP_DEBUG(this->get_logger(), 
                "Camera frame received: %dx%d", msg->width, msg->height);
        }
    }
    
    void control_loop()
    {
        auto twist_msg = geometry_msgs::msg::Twist();
        
        if (obstacle_detected_) {
            // Obstacle avoidance behavior
            twist_msg.linear.x = 0.0;  // Stop moving forward
            
            // Turn away from obstacle
            if (closest_obstacle_angle_ > 0) {
                twist_msg.angular.z = -angular_speed_;  // Turn right
            } else {
                twist_msg.angular.z = angular_speed_;   // Turn left
            }
            
            RCLCPP_INFO(this->get_logger(), "Avoiding obstacle - turning");
        } else {
            // Random wandering behavior
            twist_msg.linear.x = linear_speed_;
            
            // Add some randomness to movement
            std::uniform_real_distribution<float> dist(-0.3, 0.3);
            twist_msg.angular.z = dist(rng_);
            
            RCLCPP_DEBUG(this->get_logger(), 
                "Random wandering - linear: %.2f, angular: %.2f", 
                twist_msg.linear.x, twist_msg.angular.z);
        }
        
        cmd_vel_pub_->publish(twist_msg);
    }
    
    // Publishers
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
    
    // Subscribers
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr lidar_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Range>::SharedPtr sonar_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr camera_sub_;
    
    // Timer
    rclcpp::TimerBase::SharedPtr timer_;
    
    // Random number generator
    std::mt19937 rng_;
    
    // Control variables
    bool obstacle_detected_;
    float min_distance_;
    float linear_speed_;
    float angular_speed_;
    float lidar_min_distance_;
    float sonar_range_;
    float closest_obstacle_angle_;
};

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<RobotController>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}