WITH event_times AS (
    SELECT
        u.user_id,
        u.`group` AS experiment_group,

        MIN(CASE
            WHEN e.event_type = 'home_exposure'
            THEN e.event_time
        END) AS home_time,

        MIN(CASE
            WHEN e.event_type = 'product_click'
            THEN e.event_time
        END) AS click_time,

        MIN(CASE
            WHEN e.event_type = 'add_to_cart'
            THEN e.event_time
        END) AS cart_time,

        MIN(CASE
            WHEN e.event_type = 'purchase'
            THEN e.event_time
        END) AS purchase_time

    FROM users u
    LEFT JOIN events e
        ON u.user_id = e.user_id
        AND e.event_time >= u.register_time
        AND e.event_time < DATE_ADD(
            u.register_time, INTERVAL 7 DAY
        )
    GROUP BY u.user_id, u.`group`
),

user_funnel AS (
    SELECT
        user_id,
        experiment_group,

        CASE WHEN home_time IS NOT NULL
            THEN 1 ELSE 0 END AS exposed,

        CASE WHEN home_time IS NOT NULL
            AND click_time >= home_time
            THEN 1 ELSE 0 END AS clicked,

        CASE WHEN click_time IS NOT NULL
            AND cart_time >= click_time
            THEN 1 ELSE 0 END AS added_to_cart,

        CASE WHEN cart_time IS NOT NULL
            AND purchase_time >= cart_time
            THEN 1 ELSE 0 END AS purchased

    FROM event_times
)

SELECT
    experiment_group,
    COUNT(*) AS total_users,
    SUM(exposed) AS exposed_users,
    SUM(clicked) AS clicked_users,
    SUM(added_to_cart) AS cart_users,
    SUM(purchased) AS purchased_users,

    ROUND(
        100.0 * SUM(clicked)
        / NULLIF(SUM(exposed), 0), 2
    ) AS click_rate_pct,

    ROUND(
        100.0 * SUM(added_to_cart)
        / NULLIF(SUM(clicked), 0), 2
    ) AS cart_conversion_pct,

    ROUND(
        100.0 * SUM(purchased)
        / NULLIF(SUM(added_to_cart), 0), 2
    ) AS payment_conversion_pct,

    ROUND(
        100.0 * SUM(purchased)
        / NULLIF(SUM(exposed), 0), 2
    ) AS overall_conversion_pct

FROM user_funnel
GROUP BY experiment_group
ORDER BY experiment_group;