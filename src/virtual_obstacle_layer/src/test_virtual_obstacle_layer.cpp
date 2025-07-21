#include "rclcpp/rclcpp.hpp"
#include "pluginlib/class_loader.hpp"
#include "nav2_costmap_2d/layer.hpp"
#include "../include/virtual_obstacle_layer/virtual_obstacle_layer.hpp"
#include <memory>

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);

    pluginlib::ClassLoader<nav2_costmap_2d::Layer> loader("virtual_obstacle_layer", "nav2_costmap_2d::Layer");

    try
    {
        std::shared_ptr<nav2_costmap_2d::Layer> layer =
            loader.createSharedInstance("virtual_obstacle_layer::VirtualObstacleLayer");

        // ⚠️ 不需要调用 onInitialize，这会由 costmap 自动调用
        RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Plugin loaded successfully.");
    }
    catch (const pluginlib::PluginlibException &ex)
    {
        RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Failed to load plugin: %s", ex.what());
    }

    rclcpp::shutdown();
    return 0;
}
