#include "my_robot_serial_driver/serial_driver_node.hpp"
#include <sstream>

namespace my_robot_serial_driver
{

    SerialDriver::SerialDriver() : Node("serial_driver_node")
    {
        this->declare_parameter<std::string>("port", "/dev/ttyACM0");
        this->declare_parameter<int>("baudrate", 9600);

        std::string port;
        int baudrate;
        this->get_parameter("port", port);
        this->get_parameter("baudrate", baudrate);

        serial_fd_ = open(port.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
        if (serial_fd_ == -1)
        {
            RCLCPP_ERROR(this->get_logger(), "Failed to open serial port: %s", port.c_str());
            rclcpp::shutdown();
            return;
        }
        struct termios tty;

        if (tcgetattr(serial_fd_, &tty) != 0)
        {
            perror("tcgetattr");
            return;
        }

        fcntl(serial_fd_, F_SETFL, 0);
        struct termios options;
        tcgetattr(serial_fd_, &options);
        cfsetispeed(&options, baudrate);
        cfsetospeed(&options, baudrate);
        options.c_cflag |= (CLOCAL | CREAD);
        options.c_cflag &= ~CSIZE;
        options.c_cflag |= CS8;
        options.c_cflag &= ~PARENB;
        options.c_cflag &= ~CSTOPB;
        options.c_cflag &= ~CRTSCTS;
        tcsetattr(serial_fd_, TCSANOW, &options);

        cmd_vel_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10,
            std::bind(&SerialDriver::cmdVelCallback, this, std::placeholders::_1));

        RCLCPP_INFO(this->get_logger(), "Serial driver initialized on %s", port.c_str());
    }

    SerialDriver::~SerialDriver()
    {
        close(serial_fd_);
    }

    void SerialDriver::cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg)
    {
        float linear = msg->linear.x;
        float angular = msg->angular.z;

        std::stringstream ss;
        ss << "V " << linear << " " << angular << "\n";
        std::string cmd = ss.str();

        write(serial_fd_, cmd.c_str(), cmd.length());

        RCLCPP_INFO(this->get_logger(), "发送串口: %s", cmd.c_str());
    }

} // namespace my_robot_serial_driver

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<my_robot_serial_driver::SerialDriver>());
    rclcpp::shutdown();
    return 0;
}
