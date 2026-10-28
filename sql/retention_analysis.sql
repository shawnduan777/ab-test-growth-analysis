SELECT
    u.`group` AS experiment_group,
    COUNT(DISTINCT u.user_id) AS total_users,

    COUNT(DISTINCT CASE
        WHEN a.activity_day = 1 THEN a.user_id
    END) AS d1_active_users,

    ROUND(
        100.0 * COUNT(DISTINCT CASE
            WHEN a.activity_day = 1 THEN a.user_id
        END) / COUNT(DISTINCT u.user_id),
        2
    ) AS d1_retention_pct,

    COUNT(DISTINCT CASE
        WHEN a.activity_day = 7 THEN a.user_id
    END) AS d7_active_users,

    ROUND(
        100.0 * COUNT(DISTINCT CASE
            WHEN a.activity_day = 7 THEN a.user_id
        END) / COUNT(DISTINCT u.user_id),
        2
    ) AS d7_retention_pct

FROM users u
LEFT JOIN activity a
    ON u.user_id = a.user_id
GROUP BY u.`group`
ORDER BY u.`group`;