-- ============================================
-- 每日指标物化视图 (优化 DAU/对局/收入查询)
-- ============================================
-- 原理: game_events 每次 INSERT 时，物化视图自动触发聚合
-- 拆成两个物化视图以解决 uniq() 在 SummingMergeTree 合并时不准确的问题

-- ============================================
-- 一、每日指标聚合 (优化 event_count / revenue 查询)
-- ============================================
-- 引擎: SummingMergeTree - 相同主键的数值列自动求和

CREATE TABLE IF NOT EXISTS daily_metrics (
    event_date Date,
    event_name String,
    event_count UInt64,
    revenue Float32
) ENGINE = SummingMergeTree()
ORDER BY (event_date, event_name);

CREATE MATERIALIZED VIEW IF NOT EXISTS daily_metrics_mv
TO daily_metrics
AS SELECT
    toDate(event_time) AS event_date,
    event_name,
    count() AS event_count,
    sum(toFloat32OrNull(properties['price'])) AS revenue
FROM game_events
GROUP BY event_date, event_name;

-- ============================================
-- 二、每日活跃用户 (优化 DAU 查询)
-- ============================================
-- 引擎: ReplacingMergeTree - 相同 (date, user_id) 去重

CREATE TABLE IF NOT EXISTS daily_active_users (
    event_date Date,
    user_id String
) ENGINE = ReplacingMergeTree()
ORDER BY (event_date, user_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS daily_active_users_mv
TO daily_active_users
AS SELECT
    toDate(event_time) AS event_date,
    user_id
FROM game_events;

-- ============================================
-- 三、历史数据回填 (首次创建后执行一次)
-- ============================================

-- 回填 daily_metrics
-- INSERT INTO daily_metrics
-- SELECT
--     toDate(event_time) AS event_date,
--     event_name,
--     count() AS event_count,
--     sum(toFloat32OrNull(properties['price'])) AS revenue
-- FROM game_events
-- GROUP BY event_date, event_name;

-- 回填 daily_active_users
-- INSERT INTO daily_active_users
-- SELECT DISTINCT
--     toDate(event_time) AS event_date,
--     user_id
-- FROM game_events;

-- ============================================
-- 四、查询示例
-- ============================================
-- 今日 DAU:    SELECT count() FROM daily_active_users WHERE event_date = today()
-- 今日对局:    SELECT event_count FROM daily_metrics WHERE event_date = today() AND event_name = 'match_end'
-- 今日收入:    SELECT sum(revenue) FROM daily_metrics WHERE event_date = today() AND event_name = 'skin_buy'

-- ============================================
-- 五、验证数据一致性
-- ============================================
-- SELECT
--     'daily_metrics' as source,
--     sum(event_count) as total_events,
--     sum(revenue) as total_revenue
-- FROM daily_metrics
-- UNION ALL
-- SELECT
--     'game_events' as source,
--     count() as total_events,
--     sum(toFloat32OrNull(properties['price'])) as total_revenue
-- FROM game_events;
