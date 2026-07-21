import pymysql

# ===================================================
# 🛠️ Database connection details
# ===================================================
conn = pymysql.connect(
    host='localhost',
    user='latmfks',
    password='latmfks',
    db='latmfks',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:

        # ===================================================
        # 1. Players_who_visited
        # ===================================================
        cursor.execute("DROP TABLE IF EXISTS Players_who_visited;")
        cursor.execute("""
        CREATE TABLE Players_who_visited AS
        SELECT 
            u.id AS id,
            u.global_id,
            u.FirstName,
            u.LastName,
            u.City AS City,
            mc1.city AS UserCityName,
            pr.project_city_id,
            mc2.city AS ProjectCityName,
            pr.id AS registration_id,
            pr.project_id,
            apit.id AS assign_id,
            apit.player_position_id,
            u.Position,
            u.SecondaryPosition,
            u.LevelData,
            u.Dob,
            u.PreferenceFoot,
            u.Height,
            u.Height_unit,
            u.Gender,
            u.Weight,
            u.Weight_unit,
            u.season,
            u.source,
            u.error
        FROM users_all u
        LEFT JOIN project_registration pr ON pr.player_id = u.id
        LEFT JOIN assign_player_in_team apit ON apit.registration_id = pr.id
        LEFT JOIN mastercity mc1 ON u.City = mc1.id
        LEFT JOIN project_city pc ON pr.project_city_id = pc.id
        LEFT JOIN mastercity mc2 ON pc.city_id = mc2.id
        WHERE u.OrgnRef IS NULL;
        """)

        # ===================================================
        # 2. ZonalPlayers
        # ===================================================
        cursor.execute("DROP TABLE IF EXISTS ZonalPlayers;")
        cursor.execute("""
        CREATE TABLE ZonalPlayers AS
        SELECT 
            u.id AS id,
            u.global_id,
            u.FirstName,
            u.LastName,
            u.City AS City,
            mc1.city AS UserCityName,
            apit.project_city_id,
            mc2.city AS ProjectCityName,
            apit.registration_id,
            apit.project_id,
            apit.id AS assign_id,
            apit.player_position_id,
            u.Position,
            u.SecondaryPosition,
            u.LevelData,
            u.Dob,
            u.PreferenceFoot,
            u.Height,
            u.Height_unit,
            u.Gender,
            u.Weight,
            u.Weight_unit,
            u.season,
            u.source,
            u.error
        FROM assign_player_in_team apit
        JOIN users_all u ON apit.player_id = u.id
        LEFT JOIN mastercity mc1 ON u.City = mc1.id
        LEFT JOIN project_city pc ON apit.project_city_id = pc.id
        LEFT JOIN mastercity mc2 ON pc.city_id = mc2.id
        WHERE apit.project_id IN (38, 39, 40, 42, 43);
        """)

        # ===================================================
        # 3. Players_with_a_profile
        # ===================================================
        cursor.execute("DROP TABLE IF EXISTS Players_with_a_profile;")
        cursor.execute("""
        CREATE TABLE Players_with_a_profile AS
        SELECT 
            u.id AS id,
            u.global_id,
            u.FirstName,
            u.LastName,
            u.City AS City,
            mc1.city AS UserCityName,
            pr.project_city_id,
            mc2.city AS ProjectCityName,
            pr.id AS registration_id,
            pr.project_id,
            apit.id AS assign_id,
            apit.player_position_id,
            u.Position,
            u.SecondaryPosition,
            u.LevelData,
            u.Dob,
            u.PreferenceFoot,
            u.Height,
            u.Height_unit,
            u.Gender,
            u.Weight,
            u.Weight_unit,
            u.season,
            u.source,
            u.error
        FROM project_registration pr
        JOIN users_all u ON pr.player_id = u.id
        LEFT JOIN assign_player_in_team apit ON apit.registration_id = pr.id
        LEFT JOIN mastercity mc1 ON u.City = mc1.id
        LEFT JOIN project_city pc ON pr.project_city_id = pc.id
        LEFT JOIN mastercity mc2 ON pc.city_id = mc2.id
        WHERE u.OrgnRef IS NULL;
        """)

        # ===================================================
        # 4. AllPlayers_ScoutingReports_Detailed
        # ===================================================
        cursor.execute("DROP TABLE IF EXISTS AllPlayers_ScoutingReports_Detailed;")
        cursor.execute("""
        CREATE TABLE AllPlayers_ScoutingReports_Detailed AS
        SELECT
            u.global_id AS player_global_id,
            u.FirstName,
            u.LastName,
            mc_user.city AS UserCityName,
            ms_user.name AS UserStateName,
            u.Height,
            u.Height_unit,
            u.Weight,
            u.Weight_unit,
            u.LevelData,
            u.PreferenceFoot,
            apit.project_id,
            apit.project_city_id,
            mc_project.city AS ProjectCityName,
            ms_project.name AS ProjectStateName,
            u.Position AS PositionID,
            mp_pos.description AS PositionName,
            u.SecondaryPosition AS SecondaryPositionID,
            mp_sec.description AS SecondaryPositionName,
            apit.player_position_id AS AssignedPositionID,
            mp_assign.description AS AssignedPositionName,
            pr.id AS report_id,
            prcr.report_category_id,
            rc.name AS ReportCategoryName,
            prcr.remark_value,
            prr.rating_parameter_id,
            rp.name AS RatingParameterName,
            prr.rating_value,
            prcr.remark_value AS FinalPlayerRemark
        FROM project_report pr
        JOIN assign_player_in_team apit ON pr.assign_player_id = apit.id
        JOIN users_all u ON apit.player_id = u.id
        LEFT JOIN mastercity mc_user ON u.City = mc_user.id
        LEFT JOIN masterstate ms_user ON mc_user.state = ms_user.id
        LEFT JOIN project_city pc ON apit.project_city_id = pc.id
        LEFT JOIN mastercity mc_project ON pc.city_id = mc_project.id
        LEFT JOIN masterstate ms_project ON mc_project.state = ms_project.id
        LEFT JOIN masterposition mp_pos ON u.Position = mp_pos.id
        LEFT JOIN masterposition mp_sec ON u.SecondaryPosition = mp_sec.id
        LEFT JOIN masterposition mp_assign ON apit.player_position_id = mp_assign.id
        LEFT JOIN project_report_category_remark prcr ON pr.id = prcr.report_id
        LEFT JOIN report_category rc ON prcr.report_category_id = rc.id
        LEFT JOIN project_report_rating prr ON pr.id = prr.report_id
        LEFT JOIN rating_parameter rp 
            ON prr.rating_parameter_id = rp.id
            AND rp.report_category_id = rc.id
        WHERE rp.id IS NOT NULL
        ORDER BY u.global_id, rc.name, rp.id;
        """)

        # ===================================================
        # 5. ZonalPlayers_ScoutingReports_Detailed
        # ===================================================
        cursor.execute("DROP TABLE IF EXISTS ZonalPlayers_ScoutingReports_Detailed;")
        cursor.execute("""
        CREATE TABLE ZonalPlayers_ScoutingReports_Detailed AS
        SELECT
            zp.global_id AS player_global_id,
            zp.FirstName,
            zp.LastName,
            mc_user.city AS UserCityName,
            ms_user.name AS UserStateName,
            zp.Height,
            zp.Height_unit,   
            zp.Weight,
            zp.Weight_unit,
            zp.LevelData,
            zp.PreferenceFoot,
            apit.project_id,
            apit.project_city_id,
            mc_project.city AS ProjectCityName,
            ms_project.name AS ProjectStateName,
            zp.Position AS PositionID,
            mp_pos.description AS PositionName,
            zp.SecondaryPosition AS SecondaryPositionID,
            mp_sec.description AS SecondaryPositionName,
            apit.player_position_id AS AssignedPositionID,
            mp_assign.description AS AssignedPositionName,
            pr.id AS report_id,
            prcr.report_category_id,
            rc.name AS ReportCategoryName,
            prcr.remark_value,
            prr.rating_parameter_id,
            rp.name AS RatingParameterName,
            prr.rating_value,
            prcr.remark_value AS FinalPlayerRemark
        FROM ZonalPlayers zp
        JOIN assign_player_in_team apit ON zp.assign_id = apit.id
        JOIN project_report pr ON pr.assign_player_id = apit.id
        LEFT JOIN mastercity mc_user ON zp.City = mc_user.id
        LEFT JOIN masterstate ms_user ON mc_user.state = ms_user.id
        LEFT JOIN project_city pc ON apit.project_city_id = pc.id
        LEFT JOIN mastercity mc_project ON pc.city_id = mc_project.id
        LEFT JOIN masterstate ms_project ON mc_project.state = ms_project.id
        LEFT JOIN masterposition mp_pos ON zp.Position = mp_pos.id
        LEFT JOIN masterposition mp_sec ON zp.SecondaryPosition = mp_sec.id
        LEFT JOIN masterposition mp_assign ON apit.player_position_id = mp_assign.id
        LEFT JOIN project_report_category_remark prcr ON pr.id = prcr.report_id
        LEFT JOIN report_category rc ON prcr.report_category_id = rc.id
        LEFT JOIN project_report_rating prr ON pr.id = prr.report_id
        LEFT JOIN rating_parameter rp 
            ON prr.rating_parameter_id = rp.id
            AND rp.report_category_id = rc.id
        WHERE rp.id IS NOT NULL
        ORDER BY zp.global_id, rc.name, rp.id;
        """)

        # ===================================================
        # 6. Table: AgeGroupCounts_Season4_5
        # ===================================================
        cursor.execute("DROP VIEW IF EXISTS AgeGroupCounts_Season4_5;")
        cursor.execute("DROP TABLE IF EXISTS AgeGroupCounts_Season4_5;")
        cursor.execute("""
        CREATE TABLE AgeGroupCounts_Season4_5 AS
        SELECT 
            CASE 
                WHEN TIMESTAMPDIFF(YEAR, p.Dob, 
                    CASE 
                        WHEN u.season = 5 THEN '2025-02-01' 
                        ELSE CURDATE() 
                    END
                ) <= 13 THEN 'U13'
                WHEN TIMESTAMPDIFF(YEAR, p.Dob, 
                    CASE 
                        WHEN u.season = 5 THEN '2025-02-01' 
                        ELSE CURDATE() 
                    END
                ) <= 15 THEN 'U15'
                ELSE 'U17'
            END AS AgeGroup,
            COUNT(*) AS Count
        FROM players_with_a_profile p
        JOIN users_all u ON p.id = u.id
        WHERE u.season IN (4,5) AND p.Dob IS NOT NULL
        GROUP BY AgeGroup;
        """)

        # ===================================================
        # 7. Table: ZonalPlayers_HeightWeightConverted
        # ===================================================
        cursor.execute("DROP VIEW IF EXISTS ZonalPlayers_HeightWeightConverted;")
        cursor.execute("DROP TABLE IF EXISTS ZonalPlayers_HeightWeightConverted;")
        cursor.execute("""
        CREATE TABLE ZonalPlayers_HeightWeightConverted AS
        SELECT
            id,
            global_id,
            FirstName,
            LastName,
            Gender,
            Position,
            CAST(
                CASE 
                    WHEN Height_unit = 'inc' AND Height IS NOT NULL THEN Height * 2.54
                    ELSE Height
                END AS DECIMAL(5,2)
            ) AS Height_cm,
            CAST(
                CASE
                    WHEN Weight_unit = 'pnd' AND Weight IS NOT NULL THEN Weight * 0.453592
                    ELSE Weight
                END AS DECIMAL(5,2)
            ) AS Weight_kg
        FROM ZonalPlayers
        WHERE Height IS NOT NULL 
        AND Weight IS NOT NULL
        AND Gender IS NOT NULL 
        AND Position IS NOT NULL;
        """)

        # ===================================================
        # 8. Table: Top5States_AvgRating (no window function)
        # ===================================================
        cursor.execute("DROP VIEW IF EXISTS Top5States_AvgRating;")
        cursor.execute("DROP TABLE IF EXISTS Top5States_AvgRating;")
        cursor.execute("""
        CREATE TABLE Top5States_AvgRating AS
        SELECT 
            ProjectStateName AS State,
            AVG(rating_value) AS AvgRating
        FROM allplayers_scoutingreports_detailed
        WHERE ProjectStateName IS NOT NULL AND rating_value IS NOT NULL
        GROUP BY ProjectStateName
        ORDER BY AvgRating DESC
        LIMIT 5;
        """)

        # ===================================================
        # 9. Table: PositionImpact_AvgRating_ShortForms
        # ===================================================
        cursor.execute("DROP VIEW IF EXISTS PositionImpact_AvgRating_ShortForms;")
        cursor.execute("DROP TABLE IF EXISTS PositionImpact_AvgRating_ShortForms;")
        cursor.execute("""CREATE TABLE PositionImpact_AvgRating_ShortForms AS
        SELECT
        PositionName,
        CASE
            WHEN PositionName = AssignedPositionName THEN 'In Position'
            ELSE 'Out of Position'
        END AS PositionStatus,
        CASE PositionName
            WHEN 'Attacking Midfielder' THEN 'AM'
            WHEN 'Center Back' THEN 'CB'
            WHEN 'Central Forward/Striker' THEN 'CF'
            WHEN 'Central Midfielder' THEN 'CM'
            WHEN 'Defensive Midfielder' THEN 'DM'
            WHEN 'Goal Keeper' THEN 'GK'
            WHEN 'Left Back' THEN 'LB'
            WHEN 'Left Midfielder' THEN 'LM'
            WHEN 'Left Wing' THEN 'LW'
            WHEN 'Right Back' THEN 'RB'
            WHEN 'Right Midfielder' THEN 'RM'
            WHEN 'Right Wing' THEN 'RW'
            ELSE PositionName
        END AS PositionShort,
        AVG(avg_rating) AS AvgRating
        FROM (
        SELECT
            PositionName,
            AssignedPositionName,
            AVG(rating_value) AS avg_rating
        FROM allplayers_scoutingreports_detailed
        WHERE rating_value <= 5
            AND PositionName IS NOT NULL
            AND AssignedPositionName IS NOT NULL
        GROUP BY PositionName, AssignedPositionName
        ) AS sub
        GROUP BY PositionName, PositionStatus, PositionShort;
        """)

        # ===================================================
        # 10. Table: TopVsAvg_PerformerRadar (no window functions)
        # ===================================================
        # Create intermediate table
        cursor.execute("DROP TABLE IF EXISTS PlayerCategoryAvg;")
        cursor.execute("""
        CREATE TABLE PlayerCategoryAvg AS
        SELECT 
            player_global_id,
            AssignedPositionName,
            ReportCategoryName,
            AVG(rating_value) AS avg_rating,
            SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END) AS total_5s,
            COUNT(*) AS total_reports
        FROM allplayers_scoutingreports_detailed
        WHERE rating_value <= 5
        AND AssignedPositionName IS NOT NULL
        AND ReportCategoryName IS NOT NULL
        AND player_global_id IS NOT NULL
        GROUP BY player_global_id, AssignedPositionName, ReportCategoryName;
        """)

        # Final table creation without window function
        cursor.execute("DROP VIEW IF EXISTS TopVsAvg_PerformerRadar;")
        cursor.execute("DROP TABLE IF EXISTS TopVsAvg_PerformerRadar;")
        cursor.execute("""
        CREATE TABLE TopVsAvg_PerformerRadar AS
        SELECT 
            AssignedPositionName,
            ReportCategoryName,
            MAX(avg_rating) AS TopPerformer,
            AVG(avg_rating) AS AvgPerformer
        FROM PlayerCategoryAvg
        WHERE total_5s < total_reports
        GROUP BY AssignedPositionName, ReportCategoryName;
        """)

        # ===================================================
        # 11. Table: FootPreferenceCounts
        # ===================================================
        cursor.execute("DROP VIEW IF EXISTS FootPreferenceCounts;")
        cursor.execute("DROP TABLE IF EXISTS FootPreferenceCounts;")
        cursor.execute("""
        CREATE TABLE FootPreferenceCounts AS
        SELECT
            PreferenceFoot,
            COUNT(*) AS Count
        FROM players_who_visited
        WHERE PreferenceFoot IS NOT NULL
        GROUP BY PreferenceFoot;
        """)

        # ===================================================
        # 12. Table: Monthly_Cumulative_Registrations (no window functions)
        # ===================================================
        cursor.execute("DROP VIEW IF EXISTS Monthly_Cumulative_Registrations;")
        cursor.execute("DROP TABLE IF EXISTS Monthly_Cumulative_Registrations;")
        cursor.execute("""
        CREATE TABLE Monthly_Cumulative_Registrations AS
        SELECT
            DATE_FORMAT(created_at, '%Y-%m') AS Month,
            COUNT(*) AS Registrations,
            YEAR(created_at) AS Year,
            MONTH(created_at) AS MonthNum
        FROM users_all
        WHERE created_at IS NOT NULL
        GROUP BY Month, Year, MonthNum
        ORDER BY Month;
        """)
        # Note: Calculate cumulative sum in Python after loading this table.

        # ===================================================
        # 13. Table: SecondaryPositionPreferenceCounts
        # ===================================================
        cursor.execute("DROP VIEW IF EXISTS SecondaryPositionPreferenceCounts;")
        cursor.execute("DROP TABLE IF EXISTS SecondaryPositionPreferenceCounts;")
        cursor.execute("""
        CREATE TABLE SecondaryPositionPreferenceCounts AS
        SELECT
            CASE Position
                WHEN 'Attacking_Midfielder' THEN 'AM'
                WHEN 'Center_Back' THEN 'CB'
                WHEN 'Central_Forward_Striker' THEN 'CF'
                WHEN 'Central_Midfielder' THEN 'CM'
                WHEN 'Defensive_Midfielder' THEN 'DM'
                WHEN 'Goal_Keeper' THEN 'GK'
                WHEN 'Left_Back' THEN 'LB'
                WHEN 'Left_Midfielder' THEN 'LM'
                WHEN 'Left_Wing' THEN 'LW'
                WHEN 'Right_Back' THEN 'RB'
                WHEN 'Right_Midfielder' THEN 'RM'
                WHEN 'Right_Wing' THEN 'RW'
                ELSE Position
            END AS PositionShort,
            CASE SecondaryPosition
                WHEN 'Attacking_Midfielder' THEN 'AM'
                WHEN 'Center_Back' THEN 'CB'
                WHEN 'Central_Forward_Striker' THEN 'CF'
                WHEN 'Central_Midfielder' THEN 'CM'
                WHEN 'Defensive_Midfielder' THEN 'DM'
                WHEN 'Goal_Keeper' THEN 'GK'
                WHEN 'Left_Back' THEN 'LB'
                WHEN 'Left_Midfielder' THEN 'LM'
                WHEN 'Left_Wing' THEN 'LW'
                WHEN 'Right_Back' THEN 'RB'
                WHEN 'Right_Midfielder' THEN 'RM'
                WHEN 'Right_Wing' THEN 'RW'
                ELSE SecondaryPosition
            END AS SecondaryPositionShort,
            COUNT(*) AS Count
        FROM players_with_a_profile
        WHERE Position IS NOT NULL
        AND SecondaryPosition IS NOT NULL
        AND Position != SecondaryPosition
        GROUP BY PositionShort, SecondaryPositionShort
        ORDER BY PositionShort, Count DESC;
        """)

    conn.commit()
    print("✅ All 5 tables recreated successfully!")

finally:
    conn.close()
