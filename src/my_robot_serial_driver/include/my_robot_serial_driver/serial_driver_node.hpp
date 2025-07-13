#ifndef MY_ROBOT_SERIAL_DRIVER__SERIAL_DRIVER_NODE_HPP_
#define MY_ROBOT_SERIAL_DRIVER__SERIAL_DRIVER_NODE_HPP_

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <string>

namespace my_robot_serial_driver
{

    class SerialDriver : public rclcpp::Node
    {
    public:
        SerialDriver();
        ~SerialDriver();

    private:
        void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg);
        int serial_fd_;

        rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
    };

} // namespace my_robot_serial_driver

#endif // MY_ROBOT_SERIAL_DRIVER__SERIAL_DRIVER_NODE_HPP_
