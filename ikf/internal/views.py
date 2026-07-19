from django.shortcuts import render
from django.db import connections
import pandas as pd
from django.http import HttpResponse
from django.template import loader
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import loader

def dashboard_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('internal_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def dashboard_logout(request):
    logout(request)
    return redirect('dashboard_login')

@login_required(login_url='/internal/login/')
def internal_dashboard(request):
    context = dict()

    # =====================================================
    # FETCHING DROPDOWN OPTIONS FROM DATABASE
    # =====================================================
    with connections['latmfks'].cursor() as cursor:
        cursor.execute("SELECT DISTINCT Gender FROM users_all WHERE Gender IS NOT NULL AND Gender != ''")
        genders = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Height FROM users_all WHERE Height IS NOT NULL AND Height != ''")
        heights = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Weight FROM users_all WHERE Weight IS NOT NULL AND Weight != ''")
        weights = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT LevelData FROM users_all WHERE LevelData IS NOT NULL AND LevelData != ''")
        leveldatas = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Position FROM users_all WHERE Position IS NOT NULL AND Position != ''")
        positions = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT SecondaryPosition FROM users_all WHERE SecondaryPosition IS NOT NULL AND SecondaryPosition != ''")
        secondary_positions = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT season FROM users_all WHERE season IS NOT NULL")
        seasons = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT id, name FROM masterstate ORDER BY name")
        states = cursor.fetchall()

    # =====================================================
    # FETCHING CITY DROPDOWN BASED ON STATE (if selected)
    # =====================================================
    state_id = request.GET.get('state')
    with connections['latmfks'].cursor() as cursor:
        if state_id:
            cursor.execute("SELECT id, city FROM mastercity WHERE state = %s ORDER BY city", [state_id])
        else:
            cursor.execute("SELECT id, city FROM mastercity ORDER BY city")
        cities = cursor.fetchall()

    # =====================================================
    # BUILDING FILTERED QUERY
    # =====================================================
    filters = []
    params = []

    gender = request.GET.get('gender')
    if gender:
        filters.append("u.Gender = %s")
        params.append(gender)

    if state_id:
        filters.append("mc.state = %s")
        params.append(state_id)

    city_id = request.GET.get('city')
    if city_id:
        filters.append("u.City = %s")
        params.append(city_id)

    height_min = request.GET.get('height_min')
    height_max = request.GET.get('height_max')
    if height_min and height_max:
        filters.append("CAST(u.Height AS UNSIGNED) BETWEEN %s AND %s")
        params.extend([height_min, height_max])
    elif height_min:
        filters.append("CAST(u.Height AS UNSIGNED) >= %s")
        params.append(height_min)
    elif height_max:
        filters.append("CAST(u.Height AS UNSIGNED) <= %s")
        params.append(height_max)

    weight_min = request.GET.get('weight_min')
    weight_max = request.GET.get('weight_max')
    if weight_min and weight_max:
        filters.append("CAST(u.Weight AS UNSIGNED) BETWEEN %s AND %s")
        params.extend([weight_min, weight_max])
    elif weight_min:
        filters.append("CAST(u.Weight AS UNSIGNED) >= %s")
        params.append(weight_min)
    elif weight_max:
        filters.append("CAST(u.Weight AS UNSIGNED) <= %s")
        params.append(weight_max)

    leveldata = request.GET.get('leveldata')
    if leveldata:
        filters.append("u.LevelData = %s")
        params.append(leveldata)

    position = request.GET.get('position')
    if position:
        filters.append("u.Position = %s")
        params.append(position)

    secondary_position = request.GET.get('secondary_position')
    if secondary_position:
        filters.append("u.SecondaryPosition = %s")
        params.append(secondary_position)

    season = request.GET.get('season')
    if season:
        filters.append("u.season = %s")
        params.append(season)

    age_group = request.GET.get('age_group')
    today = datetime.date.today()
    if age_group:
        if age_group == 'u13':
            max_dob = today.replace(year=today.year-13)
            min_dob = today.replace(year=today.year-14)
        elif age_group == 'u15':
            max_dob = today.replace(year=today.year-15)
            min_dob = today.replace(year=today.year-16)
        elif age_group == 'u17':
            max_dob = today.replace(year=today.year-17)
            min_dob = today.replace(year=today.year-18)
        filters.append("u.Dob BETWEEN %s AND %s")
        params.extend([min_dob, max_dob])

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    # =====================================================
    # BUILD QUERY
    # =====================================================
    base_query = f"""
        SELECT u.global_id, u.FirstName, u.LastName, u.Gender,
               mc.city AS City, ms.name AS State,
               u.Height, u.Weight, u.LevelData, u.Position, u.SecondaryPosition, u.season
        FROM users_all u
        LEFT JOIN mastercity mc ON u.City = mc.id
        LEFT JOIN masterstate ms ON mc.state = ms.id
        {where_clause}
    """

    # =====================================================
    # IF DOWNLOAD, NO LIMIT. ELSE LIMIT 500 FOR DISPLAY
    # =====================================================
    if 'download' in request.GET:
        query = base_query
    else:
        query = base_query + " LIMIT 500;"

    with connections['latmfks'].cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=columns)

    # =====================================================
    # HANDLE DOWNLOAD REQUEST
    # =====================================================
    if 'download' in request.GET:
        file_type = request.GET.get('download')
        if file_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users_all.csv"'
            df.to_csv(path_or_buf=response, index=False)
            return response
        elif file_type == 'excel':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="users_all.xlsx"'
            df.to_excel(response, index=False)
            return response

    # =====================================================
    # ADD CONTEXT FOR TEMPLATE
    # =====================================================
    context.update({
        'users_all': df.to_dict(orient='records'),
        'genders': genders,
        'cities': cities,
        'heights': heights,
        'weights': weights,
        'leveldatas': leveldatas,
        'positions': positions,
        'secondary_positions': secondary_positions,
        'seasons': seasons,
        'states': states,
    })

    return render(request, 'internal_dashboard.html', context)

@login_required(login_url='/internal/login/')
def players_who_visited_view(request):
    context = dict()

    with connections['latmfks'].cursor() as cursor:
        # Dropdown options
        cursor.execute("SELECT DISTINCT Gender FROM players_who_visited WHERE Gender IS NOT NULL AND Gender != ''")
        genders = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT PreferenceFoot FROM players_who_visited WHERE PreferenceFoot IS NOT NULL AND PreferenceFoot != ''")
        foot_preferences = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Height FROM players_who_visited WHERE Height IS NOT NULL AND Height != ''")
        heights = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Weight FROM players_who_visited WHERE Weight IS NOT NULL AND Weight != ''")
        weights = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT LevelData FROM players_who_visited WHERE LevelData IS NOT NULL AND LevelData != ''")
        leveldatas = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Position FROM players_who_visited WHERE Position IS NOT NULL AND Position != ''")
        positions = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT SecondaryPosition FROM players_who_visited WHERE SecondaryPosition IS NOT NULL AND SecondaryPosition != ''")
        secondary_positions = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT season FROM players_who_visited WHERE season IS NOT NULL")
        seasons = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT p.name 
            FROM project p
            JOIN players_who_visited pwv ON pwv.project_id = p.id
            WHERE p.name IS NOT NULL AND p.name != ''
        """)
        project_names = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT mp.description
            FROM masterposition mp
            JOIN players_who_visited pwv ON pwv.player_position_id = mp.id
            WHERE mp.description IS NOT NULL AND mp.description != ''
        """)
        assigned_positions = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT UserCityName FROM players_who_visited WHERE UserCityName IS NOT NULL AND UserCityName != '' ORDER BY UserCityName")
        cities = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT ProjectCityName FROM players_who_visited WHERE ProjectCityName IS NOT NULL AND ProjectCityName != '' ORDER BY ProjectCityName")
        project_cities = [row[0] for row in cursor.fetchall()]


    # =========================
    # Filters
    # =========================
    filters = []
    params = []

    gender = request.GET.get('gender')
    if gender:
        filters.append("pwv.Gender = %s")
        params.append(gender)

    city = request.GET.get('city')
    if city:
        filters.append("pwv.UserCityName = %s")
        params.append(city)

    project_city = request.GET.get('project_city')
    if project_city:
        filters.append("pwv.ProjectCityName = %s")
        params.append(project_city)


    height_min = request.GET.get('height_min')
    height_max = request.GET.get('height_max')
    if height_min and height_max:
        filters.append("CAST(pwv.Height AS UNSIGNED) BETWEEN %s AND %s")
        params.extend([height_min, height_max])
    elif height_min:
        filters.append("CAST(pwv.Height AS UNSIGNED) >= %s")
        params.append(height_min)
    elif height_max:
        filters.append("CAST(pwv.Height AS UNSIGNED) <= %s")
        params.append(height_max)

    weight_min = request.GET.get('weight_min')
    weight_max = request.GET.get('weight_max')
    if weight_min and weight_max:
        filters.append("CAST(pwv.Weight AS UNSIGNED) BETWEEN %s AND %s")
        params.extend([weight_min, weight_max])
    elif weight_min:
        filters.append("CAST(pwv.Weight AS UNSIGNED) >= %s")
        params.append(weight_min)
    elif weight_max:
        filters.append("CAST(pwv.Weight AS UNSIGNED) <= %s")
        params.append(weight_max)

    assigned_position = request.GET.get('assigned_position')
    if assigned_position:
        filters.append("mp_assign.description = %s")
        params.append(assigned_position)

    position = request.GET.get('position')
    if position:
        filters.append("pwv.Position = %s")
        params.append(position)

    secondary_position = request.GET.get('secondary_position')
    if secondary_position:
        filters.append("pwv.SecondaryPosition = %s")
        params.append(secondary_position)

    leveldata = request.GET.get('leveldata')
    if leveldata:
        filters.append("pwv.LevelData = %s")
        params.append(leveldata)

    foot_preference = request.GET.get('foot_preference')
    if foot_preference:
        filters.append("pwv.PreferenceFoot = %s")
        params.append(foot_preference)

    season = request.GET.get('season')
    if season:
        filters.append("pwv.season = %s")
        params.append(season)

    project_name = request.GET.get('project_name')
    if project_name:
        filters.append("p.name = %s")
        params.append(project_name)

    age_group = request.GET.get('age_group')
    today = datetime.date.today()
    if age_group:
        if age_group == 'u13':
            max_dob = today.replace(year=today.year-13)
            min_dob = today.replace(year=today.year-14)
        elif age_group == 'u15':
            max_dob = today.replace(year=today.year-15)
            min_dob = today.replace(year=today.year-16)
        elif age_group == 'u17':
            max_dob = today.replace(year=today.year-17)
            min_dob = today.replace(year=today.year-18)
        filters.append("pwv.Dob BETWEEN %s AND %s")
        params.extend([min_dob, max_dob])

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    # =========================
    # Query
    # =========================
    base_query = f"""
        SELECT pwv.global_id, pwv.FirstName, pwv.LastName, pwv.UserCityName AS UserCityName,
               pwv.ProjectCityName, p.name AS ProjectName,
               pwv.assign_id, mp_assign.description AS AssignedPosition,
               pwv.Position, pwv.SecondaryPosition, pwv.LevelData, pwv.Dob, pwv.PreferenceFoot,
               pwv.Height, pwv.Weight, pwv.season
        FROM players_who_visited pwv
        LEFT JOIN project p ON pwv.project_id = p.id
        LEFT JOIN masterposition mp_assign ON pwv.player_position_id = mp_assign.id
        {where_clause}
    """

    # =========================
    # If download, no limit. Else limit 500 for display
    # =========================
    if 'download' in request.GET:
        query = base_query
    else:
        query = base_query + " LIMIT 500;"

    with connections['latmfks'].cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=columns)
    df['Dob'] = pd.to_datetime(df['Dob'], errors='coerce')
    df['Dob'] = df['Dob'].dt.strftime('%Y-%m-%d')
    df['Dob'] = df['Dob'].fillna('')


    # =========================
    # Handle download
    # =========================
    if 'download' in request.GET:
        file_type = request.GET.get('download')
        if file_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="players_who_visited.csv"'
            df.to_csv(path_or_buf=response, index=False)
            return response
        elif file_type == 'excel':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="players_who_visited.xlsx"'
            df.to_excel(response, index=False)
            return response

    # =========================
    # Context
    # =========================
    context.update({
        'players_who_visited': df.to_dict(orient='records'),
        'genders': genders,
        'cities': cities,
        'project_cities': project_cities,
        'heights': heights,
        'weights': weights,
        'positions': positions,
        'secondary_positions': secondary_positions,
        'leveldatas': leveldatas,
        'foot_preferences': foot_preferences,
        'assigned_positions': assigned_positions,
        'seasons': seasons,
        'project_names': project_names,
    })

    return render(request, 'players_who_visited.html', context)

@login_required(login_url='/internal/login/')
def players_with_a_profile_view(request):
    context = dict()

    with connections['latmfks'].cursor() as cursor:
        # Dropdown options (adjust field names if different in this table)
        cursor.execute("SELECT DISTINCT Gender FROM players_with_a_profile WHERE Gender IS NOT NULL AND Gender != ''")
        genders = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT PreferenceFoot FROM players_with_a_profile WHERE PreferenceFoot IS NOT NULL AND PreferenceFoot != ''")
        foot_preferences = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT UserCityName FROM players_with_a_profile WHERE UserCityName IS NOT NULL AND UserCityName != '' ORDER BY UserCityName")
        cities = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT ProjectCityName FROM players_with_a_profile WHERE ProjectCityName IS NOT NULL AND ProjectCityName != '' ORDER BY ProjectCityName")
        project_cities = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Height FROM players_with_a_profile WHERE Height IS NOT NULL AND Height != ''")
        heights = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Weight FROM players_with_a_profile WHERE Weight IS NOT NULL AND Weight != ''")
        weights = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT LevelData FROM players_with_a_profile WHERE LevelData IS NOT NULL AND LevelData != ''")
        leveldatas = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Position FROM players_with_a_profile WHERE Position IS NOT NULL AND Position != ''")
        positions = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT SecondaryPosition FROM players_with_a_profile WHERE SecondaryPosition IS NOT NULL AND SecondaryPosition != ''")
        secondary_positions = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT season FROM players_with_a_profile WHERE season IS NOT NULL")
        seasons = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT p.name 
            FROM project p
            JOIN players_with_a_profile pwap ON pwap.project_id = p.id
            WHERE p.name IS NOT NULL AND p.name != ''
        """)
        project_names = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT mp.description
            FROM masterposition mp
            JOIN players_with_a_profile pwap ON pwap.player_position_id = mp.id
            WHERE mp.description IS NOT NULL AND mp.description != ''
        """)
        assigned_positions = [row[0] for row in cursor.fetchall()]

    # =========================
    # Filters
    # =========================
    filters = []
    params = []

    # replicate all filter logic but replace table alias pwv -> pwap as per your FROM clause below

    gender = request.GET.get('gender')
    if gender:
        filters.append("pwap.Gender = %s")
        params.append(gender)

    city = request.GET.get('city')
    if city:
        filters.append("pwap.UserCityName = %s")
        params.append(city)

    project_city = request.GET.get('project_city')
    if project_city:
        filters.append("pwap.ProjectCityName = %s")
        params.append(project_city)

    # continue with height, weight, positions, foot_preference, season, project_name, age_group filters
    # identical to your players_who_visited_view but change table alias accordingly

    # age group filter (example)
    age_group = request.GET.get('age_group')
    today = datetime.date.today()
    if age_group:
        if age_group == 'u13':
            max_dob = today.replace(year=today.year-13)
            min_dob = today.replace(year=today.year-14)
        elif age_group == 'u15':
            max_dob = today.replace(year=today.year-15)
            min_dob = today.replace(year=today.year-16)
        elif age_group == 'u17':
            max_dob = today.replace(year=today.year-17)
            min_dob = today.replace(year=today.year-18)
        filters.append("pwap.Dob BETWEEN %s AND %s")
        params.extend([min_dob, max_dob])

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    # =========================
    # Query
    # =========================
    base_query = f"""
        SELECT pwap.global_id, pwap.FirstName, pwap.LastName, pwap.UserCityName,
               pwap.ProjectCityName, p.name AS ProjectName,
               pwap.assign_id, mp_assign.description AS AssignedPosition,
               pwap.Position, pwap.SecondaryPosition, pwap.LevelData, pwap.Dob, pwap.PreferenceFoot,
               pwap.Height, pwap.Weight, pwap.season
        FROM players_with_a_profile pwap
        LEFT JOIN project p ON pwap.project_id = p.id
        LEFT JOIN masterposition mp_assign ON pwap.player_position_id = mp_assign.id
        {where_clause}
    """

    # =========================
    # If download, no limit. Else limit 500 for display
    # =========================
    if 'download' in request.GET:
        query = base_query
    else:
        query = base_query + " LIMIT 500;"

    with connections['latmfks'].cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=columns)
    df['Dob'] = pd.to_datetime(df['Dob'], errors='coerce')
    df['Dob'] = df['Dob'].dt.strftime('%Y-%m-%d')
    df['Dob'] = df['Dob'].fillna('')

    # =========================
    # Handle download
    # =========================
    if 'download' in request.GET:
        file_type = request.GET.get('download')
        if file_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="players_with_a_profile.csv"'
            df.to_csv(path_or_buf=response, index=False)
            return response
        elif file_type == 'excel':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="players_with_a_profile.xlsx"'
            df.to_excel(response, index=False)
            return response

    # =========================
    # Context
    # =========================
    context.update({
        'players_with_a_profile': df.to_dict(orient='records'),
        'genders': genders,
        'cities': cities,
        'project_cities': project_cities,
        'heights': heights,
        'weights': weights,
        'positions': positions,
        'secondary_positions': secondary_positions,
        'leveldatas': leveldatas,
        'foot_preferences': foot_preferences,
        'assigned_positions': assigned_positions,
        'seasons': seasons,
        'project_names': project_names,
    })

    return render(request, 'players_with_a_profile.html', context)

@login_required(login_url='/internal/login/')
def zonalplayers_view(request):
    context = dict()

    with connections['latmfks'].cursor() as cursor:
        # Dropdown options
        cursor.execute("SELECT DISTINCT Gender FROM zonalplayers WHERE Gender IS NOT NULL AND Gender != ''")
        genders = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT PreferenceFoot FROM zonalplayers WHERE PreferenceFoot IS NOT NULL AND PreferenceFoot != ''")
        foot_preferences = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT UserCityName FROM zonalplayers WHERE UserCityName IS NOT NULL AND UserCityName != '' ORDER BY UserCityName")
        cities = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT ProjectCityName FROM zonalplayers WHERE ProjectCityName IS NOT NULL AND ProjectCityName != '' ORDER BY ProjectCityName")
        project_cities = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Height FROM zonalplayers WHERE Height IS NOT NULL AND Height != ''")
        heights = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Weight FROM zonalplayers WHERE Weight IS NOT NULL AND Weight != ''")
        weights = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT LevelData FROM zonalplayers WHERE LevelData IS NOT NULL AND LevelData != ''")
        leveldatas = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Position FROM zonalplayers WHERE Position IS NOT NULL AND Position != ''")
        positions = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT SecondaryPosition FROM zonalplayers WHERE SecondaryPosition IS NOT NULL AND SecondaryPosition != ''")
        secondary_positions = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT season FROM zonalplayers WHERE season IS NOT NULL")
        seasons = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT p.name 
            FROM project p
            JOIN zonalplayers zp ON zp.project_id = p.id
            WHERE p.name IS NOT NULL AND p.name != ''
        """)
        project_names = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT mp.description
            FROM masterposition mp
            JOIN zonalplayers zp ON zp.player_position_id = mp.id
            WHERE mp.description IS NOT NULL AND mp.description != ''
        """)
        assigned_positions = [row[0] for row in cursor.fetchall()]

    # =========================
    # Filters
    # =========================
    filters = []
    params = []

    gender = request.GET.get('gender')
    if gender:
        filters.append("zp.Gender = %s")
        params.append(gender)

    city = request.GET.get('city')
    if city:
        filters.append("zp.UserCityName = %s")
        params.append(city)

    project_city = request.GET.get('project_city')
    if project_city:
        filters.append("zp.ProjectCityName = %s")
        params.append(project_city)

    height_min = request.GET.get('height_min')
    height_max = request.GET.get('height_max')
    if height_min and height_max:
        filters.append("CAST(zp.Height AS UNSIGNED) BETWEEN %s AND %s")
        params.extend([height_min, height_max])
    elif height_min:
        filters.append("CAST(zp.Height AS UNSIGNED) >= %s")
        params.append(height_min)
    elif height_max:
        filters.append("CAST(zp.Height AS UNSIGNED) <= %s")
        params.append(height_max)

    weight_min = request.GET.get('weight_min')
    weight_max = request.GET.get('weight_max')
    if weight_min and weight_max:
        filters.append("CAST(zp.Weight AS UNSIGNED) BETWEEN %s AND %s")
        params.extend([weight_min, weight_max])
    elif weight_min:
        filters.append("CAST(zp.Weight AS UNSIGNED) >= %s")
        params.append(weight_min)
    elif weight_max:
        filters.append("CAST(zp.Weight AS UNSIGNED) <= %s")
        params.append(weight_max)

    assigned_position = request.GET.get('assigned_position')
    if assigned_position:
        filters.append("mp_assign.description = %s")
        params.append(assigned_position)

    position = request.GET.get('position')
    if position:
        filters.append("zp.Position = %s")
        params.append(position)

    secondary_position = request.GET.get('secondary_position')
    if secondary_position:
        filters.append("zp.SecondaryPosition = %s")
        params.append(secondary_position)

    leveldata = request.GET.get('leveldata')
    if leveldata:
        filters.append("zp.LevelData = %s")
        params.append(leveldata)

    foot_preference = request.GET.get('foot_preference')
    if foot_preference:
        filters.append("zp.PreferenceFoot = %s")
        params.append(foot_preference)

    season = request.GET.get('season')
    if season:
        filters.append("zp.season = %s")
        params.append(season)

    project_name = request.GET.get('project_name')
    if project_name:
        filters.append("p.name = %s")
        params.append(project_name)

    age_group = request.GET.get('age_group')
    today = datetime.date.today()
    if age_group:
        if age_group == 'u13':
            max_dob = today.replace(year=today.year-13)
            min_dob = today.replace(year=today.year-14)
        elif age_group == 'u15':
            max_dob = today.replace(year=today.year-15)
            min_dob = today.replace(year=today.year-16)
        elif age_group == 'u17':
            max_dob = today.replace(year=today.year-17)
            min_dob = today.replace(year=today.year-18)
        filters.append("zp.Dob BETWEEN %s AND %s")
        params.extend([min_dob, max_dob])

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    # =========================
    # Query
    # =========================
    base_query = f"""
        SELECT zp.global_id, zp.FirstName, zp.LastName, zp.UserCityName,
               zp.ProjectCityName, p.name AS ProjectName,
               zp.assign_id, mp_assign.description AS AssignedPosition,
               zp.Position, zp.SecondaryPosition, zp.LevelData, zp.Dob, zp.PreferenceFoot,
               zp.Height, zp.Weight, zp.season
        FROM zonalplayers zp
        LEFT JOIN project p ON zp.project_id = p.id
        LEFT JOIN masterposition mp_assign ON zp.player_position_id = mp_assign.id
        {where_clause}
    """

    # =========================
    # If download, no limit. Else limit 500 for display
    # =========================
    if 'download' in request.GET:
        query = base_query
    else:
        query = base_query + " LIMIT 500;"

    with connections['latmfks'].cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=columns)
    df['Dob'] = pd.to_datetime(df['Dob'], errors='coerce')
    df['Dob'] = df['Dob'].dt.strftime('%Y-%m-%d')
    df['Dob'] = df['Dob'].fillna('')

    # =========================
    # Handle download
    # =========================
    if 'download' in request.GET:
        file_type = request.GET.get('download')
        if file_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="zonalplayers.csv"'
            df.to_csv(path_or_buf=response, index=False)
            return response
        elif file_type == 'excel':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="zonalplayers.xlsx"'
            df.to_excel(response, index=False)
            return response

    # =========================
    # Context
    # =========================
    context.update({
        'zonalplayers': df.to_dict(orient='records'),
        'genders': genders,
        'cities': cities,
        'project_cities': project_cities,
        'heights': heights,
        'weights': weights,
        'positions': positions,
        'secondary_positions': secondary_positions,
        'leveldatas': leveldatas,
        'foot_preferences': foot_preferences,
        'assigned_positions': assigned_positions,
        'seasons': seasons,
        'project_names': project_names,
    })

    return render(request, 'zonalplayers.html', context)



# =====================================================
# GET CITIES FOR STATE (for AJAX city dropdown update)
# =====================================================


def get_cities_for_state(request):
    state_id = request.GET.get('state_id')
    with connections['latmfks'].cursor() as cursor:
        if state_id:
            cursor.execute("SELECT id, city FROM mastercity WHERE state = %s ORDER BY city", [state_id])
        else:
            cursor.execute("SELECT id, city FROM mastercity ORDER BY city")
        cities = cursor.fetchall()

    template = loader.get_template('partials/city_options.html')
    context = {'cities': cities}
    return HttpResponse(template.render(context, request))

