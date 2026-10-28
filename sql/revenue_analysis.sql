WITH user_revenue AS (
    SELECT
        u.user_id,
        u.`group` AS experiment_group,
        COALESCE(SUM(o.amount), 0) AS revenue,
        COUNT(o.order_id) AS order_count

    FROM users u
    LEFT JOIN orders o
        ON u.user_id = o.user_id
        AND o.order_time >= u.register_time
        AND o.order_time < DATE_ADD(
            u.register_time, INTERVAL 7 DAY
        )
    GROUP BY u.user_id, u.`group`
)

SELECT
    experiment_group,
    COUNT(*) AS total_users,
    SUM(order_count) AS total_orders,

    SUM(CASE WHEN order_count > 0
        THEN 1 ELSE 0 END) AS purchasing_users,

    ROUND(SUM(revenue), 2) AS total_revenue,

    ROUND(AVG(revenue), 2) AS arpu,

    ROUND(
        SUM(revenue) / NULLIF(SUM(order_count), 0),
        2
    ) AS aov,

    ROUND(
        SUM(revenue) /
        NULLIF(
            SUM(CASE WHEN order_count > 0
                THEN 1 ELSE 0 END), 0
        ),
        2
    ) AS revenue_per_purchasing_user

FROM user_revenue
GROUP BY experiment_group
ORDER BY experiment_group;