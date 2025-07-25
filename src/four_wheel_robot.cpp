#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "sensor_msgs/msg/range.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include <functional>
#include <algorithm>
#include <random>

class FourWheelRobot : public rclcpp::Node
{
public:
    FourWheelRobot() : Node("four_wheel_robot"), gen_(std::random_device{}()), dist_(-0.5, 0.5)
    {
        // Parameters
        this->declare_parameter("lidar_warning", 1.5);
        this->declare_parameter("lidar_emergency", 0.8);
        this->declare_parameter("sonar_threshold", 0.3);
        this->declare_parameter("normal_speed", 0.3);
        this->declare_parameter("slow_speed", 0.1);

        // subscriptions
        lidar_sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
            "lidar/scan", 10, std::bind(&FourWheelRobot::lidar_callback, this, std::placeholders::_1)
        ); 
        sonar_sub_ = this->create_subscription<sensor_msgs::msg::Range>(
            "sonar/scan", 10, std::bind(&FourWheelRobot::sonar_callback, this, std::placeholders::_1)
        );
        cam_sub_ = this->create_subscription<sensor_msgs::msg::Image>(
            "sensor/camera", 10,
            std::bind(&FourWheelRobot::camera_callback, this, std::placeholders::_1));
        
        // Publisher
        cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);

        // Control timer (10hz)
        control_timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&FourWheelRobot::control_loop, this));
    }

private:
    // sensor data
    sensor_msgs::msg::LaserScan::SharedPtr last_lidar_;
    float sonar_distance_ = std::numeric_limits<float>::infinity();
    bool obstacle_detected_ = false;

    // ROS interfaces
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr lidar_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Range>::SharedPtr sonar_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr cam_sub_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
    rclcpp::TimerBase::SharedPtr control_timer_;

    // Random number generation for emergency turns
    std::mt19937 gen_;
    std::uniform_real_distribution<float> dist_;

     void lidar_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
    {
        last_lidar_ = msg;  // Store for sector scanning
        
        // Process front arc (-60° to +60°)
        const float arc_start = -M_PI/3.0f;
        const float arc_end = M_PI/3.0f;
        
        int start_idx = (arc_start - msg->angle_min) / msg->angle_increment;
        int end_idx = (arc_end - msg->angle_min) / msg->angle_increment;
        
        start_idx = std::clamp(start_idx, 0, static_cast<int>(msg->ranges.size())-1);
        end_idx = std::clamp(end_idx, 0, static_cast<int>(msg->ranges.size())-1);

        float min_distance = std::numeric_limits<float>::infinity();
        for (int i = start_idx; i <= end_idx; ++i) {
            if (std::isfinite(msg->ranges[i])) {
                min_distance = std::min(min_distance, msg->ranges[i]);
            }
        }

        obstacle_detected_ = (min_distance < this->get_parameter("lidar_warning").as_double());
        RCLCPP_DEBUG(this->get_logger(), "Front arc min distance: %.2f m", min_distance);
    }

    void sonar_callback(const sensor_msgs::msg::Range::SharedPtr msg)
    {
        if (msg->radiation_type == msg->ULTRASOUND && std::isfinite(msg->range)) {
            sonar_distance_ = msg->range;
        } else {
            sonar_distance_ = std::numeric_limits<float>::infinity();
        }
    }

    void camera_callback(const sensor_msgs::msg::Image::SharedPtr msg) {
        // Process camera data here
        if (msg) {
            return;
        }
        return;
    }

    float scan_sector(float start_angle, float end_angle) 
    {
        if (!last_lidar_) return std::numeric_limits<float>::infinity();
        
        int start_idx = (start_angle - last_lidar_->angle_min) / last_lidar_->angle_increment;
        int end_idx = (end_angle - last_lidar_->angle_min) / last_lidar_->angle_increment;
        
        start_idx = std::clamp(start_idx, 0, static_cast<int>(last_lidar_->ranges.size())-1);
        end_idx = std::clamp(end_idx, 0, static_cast<int>(last_lidar_->ranges.size())-1);
        
        float min_dist = std::numeric_limits<float>::infinity();
        for (int i = start_idx; i <= end_idx; ++i) {
            if (std::isfinite(last_lidar_->ranges[i])) {
                min_dist = std::min(min_dist, last_lidar_->ranges[i]);
            }
        }
        return min_dist;
    }

    void control_loop()
    {
        auto cmd = geometry_msgs::msg::Twist();
        // const double lidar_warning = this->get_parameter("lidar_warning").as_double();
        // const double lidar_emergency = this->get_parameter("lidar_emergency").as_double();
        const double sonar_threshold = this->get_parameter("sonar_threshold").as_double();
        const double normal_speed = this->get_parameter("normal_speed").as_double();
        const double slow_speed = this->get_parameter("slow_speed").as_double();

        // Emergency behavior (sonar or very close obstacle)
        if (sonar_distance_ < sonar_threshold) {
            cmd.linear.x = -0.1;  // Reverse
            cmd.angular.z = dist_(gen_);  // Random turn
            RCLCPP_WARN(this->get_logger(), "Emergency: Sonar detected obstacle at %.2f m!", sonar_distance_);
        }
        // Obstacle avoidance
        else if (obstacle_detected_) {
            float left_min = scan_sector(-M_PI/2.0f, -M_PI/6.0f);  // Left sector
            float right_min = scan_sector(M_PI/6.0f, M_PI/2.0f);   // Right sector
            
            if (left_min > right_min && left_min > 0.5f) {
                cmd.linear.x = slow_speed;
                cmd.angular.z = 0.3;  // Turn left
                RCLCPP_INFO(this->get_logger(), "Avoiding right (left clear: %.2f m)", left_min);
            } 
            else if (right_min > 0.5f) {
                cmd.linear.x = slow_speed;
                cmd.angular.z = -0.3;  // Turn right
                RCLCPP_INFO(this->get_logger(), "Avoiding left (right clear: %.2f m)", right_min);
            }
            else {
                cmd.linear.x = 0.0;
                cmd.angular.z = 0.5;  // Spin in place
                RCLCPP_WARN(this->get_logger(), "No clear path - searching");
            }
        }
        // Normal operation
        else {
            cmd.linear.x = normal_speed;
            cmd.angular.z = 0.0;
        }

        cmd_vel_pub_->publish(cmd);
    }
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<FourWheelRobot>());
    rclcpp::shutdown();
    return 0;
}