WITH user_profit AS (
    SELECT
        u.user_id,
        u.`group` AS experiment_group,

        COALESCE(SUM(o.amount), 0) AS revenue,

        COALESCE(SUM(o.contribution_profit), 0)
            AS contribution_profit,

        COALESCE(SUM(o.refund_amount), 0)
            AS refund_amount,

        COUNT(o.order_id) AS order_count,

        COALESCE(SUM(o.refunded), 0)
            AS refunded_orders

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
    SUM(refunded_orders) AS refunded_orders,

    ROUND(SUM(revenue), 2) AS total_revenue,

    ROUND(
        SUM(contribution_profit), 2
    ) AS total_contribution_profit,

    ROUND(
        AVG(contribution_profit), 2
    ) AS contribution_profit_per_user,

    ROUND(
        100.0 * SUM(refunded_orders)
        / NULLIF(SUM(order_count), 0),
        2
    ) AS refund_order_rate_pct,

    ROUND(
        100.0 * SUM(refund_amount)
        / NULLIF(SUM(revenue), 0),
        2
    ) AS refund_amount_rate_pct

FROM user_profit
GROUP BY experiment_group
ORDER BY experiment_group;