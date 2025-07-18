#include "virtual_obstacle_layer/virtual_obstacle_layer.hpp"
#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(virtual_obstacle_layer::VirtualObstacleLayer, nav2_costmap_2d::Layer)

namespace virtual_obstacle_layer
{

    void VirtualObstacleLayer::onInitialize()
    {
        // 必须调用父类的初始化
        nav2_costmap_2d::Layer::onInitialize();

        // 声明并读取参数
        node_->declare_parameter("enabled", rclcpp::ParameterValue(true));
        node_->get_parameter("enabled", enabled_);

        // 调整代价地图尺寸匹配
        matchSize();
    }

    void VirtualObstacleLayer::updateBounds(
        double robot_x, double robot_y, double robot_yaw,
        double *min_x, double *min_y, double *max_x, double *max_y)
    {
        if (!enabled_)
            return;

        // 更新整个地图区域
        *min_x = 0.0;
        *min_y = 0.0;
        *max_x = 4.0;
        *max_y = 4.0;
    }
    void virtual_obstacle_layer::VirtualObstacleLayer::reset()
    {
        // 如果你没有特别逻辑，可以什么都不做
    }

    void VirtualObstacleLayer::updateCosts(
        nav2_costmap_2d::Costmap2D &master_grid,
        int min_i, int min_j, int max_i, int max_j)
    {
        if (!enabled_)
            return;

        // 地图边界参数
        double map_width = 4.0;
        double map_height = 4.0;
        double wall_thickness = 0.02; // 2cm

        // 圆形禁入区参数
        std::vector<std::pair<double, double>> circle_centers = {
            {1.0, 2.0}, {2.0, 2.0}, {3.0, 2.0}};
        double radius = 0.5; // 半径 0.5m

        // 遍历 costmap 区域
        for (int i = min_i; i < max_i; ++i)
        {
            for (int j = min_j; j < max_j; ++j)
            {
                double wx, wy;
                mapToWorld(i, j, wx, wy);

                // ==== 判断边界墙 ====
                if (wx <= wall_thickness || wx >= map_width - wall_thickness ||
                    wy <= wall_thickness || wy >= map_height - wall_thickness)
                {
                    master_grid.setCost(i, j, nav2_costmap_2d::LETHAL_OBSTACLE);
                    continue;
                }

                // ==== 判断是否在圆形障碍内 ====
                for (const auto &center : circle_centers)
                {
                    int cx = center.first;
                    int cy = center.second;

                    double dist = hypot(wx - cx, wy - cy);
                    if (dist <= radius)
                    {
                        master_grid.setCost(i, j, nav2_costmap_2d::LETHAL_OBSTACLE);
                        break;
                    }
                }
            }
        }
    }

} // namespace virtual_obstacle_layer
