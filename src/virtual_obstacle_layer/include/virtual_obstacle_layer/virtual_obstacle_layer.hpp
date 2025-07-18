#ifndef VIRTUAL_OBSTACLE_LAYER_HPP
#define VIRTUAL_OBSTACLE_LAYER_HPP

#include "nav2_costmap_2d/layer.hpp"
#include "nav2_costmap_2d/layered_costmap.hpp"
#include "nav2_costmap_2d/costmap_layer.hpp"

namespace virtual_obstacle_layer
{

    class VirtualObstacleLayer : public nav2_costmap_2d::CostmapLayer
    {
    public:
        void onInitialize() override;
        void updateBounds(
            double robot_x, double robot_y, double robot_yaw,
            double *min_x, double *min_y, double *max_x, double *max_y) override;
        void updateCosts(
            nav2_costmap_2d::Costmap2D &master_grid,
            int min_i, int min_j, int max_i, int max_j) override;
        void reset() override;

    private:
        bool enabled_;
    };

} // namespace

#endif
