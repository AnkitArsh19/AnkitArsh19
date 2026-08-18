import datetime
from dateutil import relativedelta
import requests
import os
from lxml import etree
import time
import hashlib

# Fine-grained personal access token with All Repositories access:
HEADERS = {'authorization': 'token '+ os.environ.get('ACCESS_TOKEN', '')}
USER_NAME = os.environ.get('USER_NAME', 'AnkitArsh19')
QUERY_COUNT = {'user_getter': 0, 'follower_getter': 0, 'graph_repos_stars': 0, 'recursive_loc': 0, 'graph_commits': 0, 'loc_query': 0, 'language_breakdown': 0, 'recent_activity': 0}

def daily_readme(birthday):
    diff = relativedelta.relativedelta(datetime.datetime.today(), birthday)
    return '{} {}, {} {}, {} {}{}'.format(
        diff.years, 'year' + format_plural(diff.years), 
        diff.months, 'month' + format_plural(diff.months), 
        diff.days, 'day' + format_plural(diff.days),
        ' 🎂' if (diff.months == 0 and diff.days == 0) else '')

def format_plural(unit):
    return 's' if unit != 1 else ''

def simple_request(func_name, query, variables):
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables':variables}, headers=HEADERS)
    if request.status_code == 200:
        return request
    raise Exception(func_name, ' has failed with a', request.status_code, request.text, QUERY_COUNT)

def graph_repos_stars(count_type, owner_affiliation, cursor=None, add_loc=0, del_loc=0, is_fork=None):
    query_count('graph_repos_stars')
    fork_filter = "" if is_fork is None else f", isFork: {'true' if is_fork else 'false'}"
    query = '''
    query ($owner_affiliation: [RepositoryAffiliation], $login: String!, $cursor: String) {
        user(login: $login) {
            repositories(first: 100, after: $cursor, ownerAffiliations: $owner_affiliation''' + fork_filter + ''') {
                totalCount
                edges {
                    node {
                        ... on Repository {
                            nameWithOwner
                            stargazers {
                                totalCount
                            }
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    }'''
    variables = {'owner_affiliation': owner_affiliation, 'login': USER_NAME, 'cursor': cursor}
    request = simple_request(graph_repos_stars.__name__, query, variables)
    res_json = request.json()
    user_data = res_json.get('data', {}).get('user') if res_json.get('data') else None
    if not user_data or 'repositories' not in user_data:
        return 0

    repo_data = user_data['repositories']
    if count_type == 'repos':
        return repo_data.get('totalCount', 0)
    elif count_type == 'stars':
        edges = repo_data.get('edges', []) or []
        current_stars = stars_counter(edges)
        page_info = repo_data.get('pageInfo', {})
        if page_info.get('hasNextPage'):
            return current_stars + graph_repos_stars(count_type, owner_affiliation, page_info.get('endCursor'), add_loc, del_loc, is_fork)
        return current_stars

def recursive_loc(owner, repo_name, data, cache_comment, addition_total=0, deletion_total=0, my_commits=0, cursor=None):
    query_count('recursive_loc')
    query = '''
    query ($repo_name: String!, $owner: String!, $cursor: String) {
        repository(name: $repo_name, owner: $owner) {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(first: 100, after: $cursor) {
                            totalCount
                            edges {
                                node {
                                    ... on Commit {
                                        committedDate
                                    }
                                    author {
                                        user {
                                            id
                                        }
                                    }
                                    deletions
                                    additions
                                }
                            }
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                        }
                    }
                }
            }
        }
    }'''
    variables = {'repo_name': repo_name, 'owner': owner, 'cursor': cursor}
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables':variables}, headers=HEADERS)
    if request.status_code == 200:
        res_json = request.json()
        repo = res_json.get('data', {}).get('repository') if res_json.get('data') else None
        if repo and repo.get('defaultBranchRef') and repo['defaultBranchRef'].get('target'):
            history = repo['defaultBranchRef']['target'].get('history')
            if history:
                return loc_counter_one_repo(owner, repo_name, data, cache_comment, history, addition_total, deletion_total, my_commits)
        return 0
    force_close_file(data, cache_comment)
    if request.status_code == 403:
        raise Exception('Too many requests in a short amount of time!\nYou\'ve hit the non-documented anti-abuse limit!')
    raise Exception('recursive_loc() has failed with a', request.status_code, request.text, QUERY_COUNT)

def loc_counter_one_repo(owner, repo_name, data, cache_comment, history, addition_total, deletion_total, my_commits):
    edges = history.get('edges', []) if history else []
    for node in edges:
        if not node or not isinstance(node, dict):
            continue
        commit_node = node.get('node')
        if not commit_node or not isinstance(commit_node, dict):
            continue
        author = commit_node.get('author')
        user = author.get('user') if isinstance(author, dict) else None
        if user and isinstance(user, dict) and user.get('id') == OWNER_ID.get('id'):
            my_commits += 1
            addition_total += commit_node.get('additions', 0)
            deletion_total += commit_node.get('deletions', 0)

    page_info = history.get('pageInfo', {}) if history else {}
    if not edges or not page_info.get('hasNextPage'):
        return addition_total, deletion_total, my_commits
    else:
        return recursive_loc(owner, repo_name, data, cache_comment, addition_total, deletion_total, my_commits, page_info.get('endCursor'))

def loc_query(owner_affiliation, comment_size=0, force_cache=False, cursor=None, edges=None):
    if edges is None:
        edges = []
    query_count('loc_query')
    query = '''
    query ($owner_affiliation: [RepositoryAffiliation], $login: String!, $cursor: String) {
        user(login: $login) {
            repositories(first: 60, after: $cursor, ownerAffiliations: $owner_affiliation, isFork: false) {
            edges {
                node {
                    ... on Repository {
                        nameWithOwner
                        defaultBranchRef {
                            target {
                                ... on Commit {
                                    history {
                                        totalCount
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    }'''
    variables = {'owner_affiliation': owner_affiliation, 'login': USER_NAME, 'cursor': cursor}
    request = simple_request(loc_query.__name__, query, variables)
    res_json = request.json()
    user_data = res_json.get('data', {}).get('user') if res_json.get('data') else None
    if not user_data or 'repositories' not in user_data:
        return cache_builder(edges, comment_size, force_cache)

    repo_data = user_data['repositories']
    current_edges = [e for e in (repo_data.get('edges') or []) if e and isinstance(e, dict) and e.get('node')]
    edges = edges + current_edges
    page_info = repo_data.get('pageInfo', {})
    if page_info.get('hasNextPage'):
        return loc_query(owner_affiliation, comment_size, force_cache, page_info.get('endCursor'), edges)
    else:
        return cache_builder(edges, comment_size, force_cache)

def cache_builder(edges, comment_size, force_cache, loc_add=0, loc_del=0):
    cached = True
    filename = 'cache/'+hashlib.sha256(USER_NAME.encode('utf-8')).hexdigest()+'.txt'
    if not os.path.exists('cache'):
        os.makedirs('cache')
    try:
        with open(filename, 'r') as f:
            data = f.readlines()
    except FileNotFoundError:
        data = []
        if comment_size > 0:
            for _ in range(comment_size): data.append('This line is a comment block. Write whatever you want here.\n')
        with open(filename, 'w') as f:
            f.writelines(data)

    if len(data)-comment_size != len(edges) or force_cache:
        cached = False
        flush_cache(edges, filename, comment_size)
        with open(filename, 'r') as f:
            data = f.readlines()

    cache_comment = data[:comment_size]
    data = data[comment_size:]
    for index in range(len(edges)):
        if index >= len(data):
            break
        parts = data[index].split()
        if len(parts) < 2:
            continue
        repo_hash = parts[0]
        commit_count = parts[1]
        node = edges[index].get('node') if isinstance(edges[index], dict) else None
        if not node or not node.get('nameWithOwner'):
            continue
        if repo_hash == hashlib.sha256(node['nameWithOwner'].encode('utf-8')).hexdigest():
            try:
                branch_ref = node.get('defaultBranchRef')
                target = branch_ref.get('target') if branch_ref else None
                history = target.get('history') if target else None
                total_count = history.get('totalCount') if history else None
                if total_count is not None and int(commit_count) != total_count:
                    owner, repo_name = node['nameWithOwner'].split('/')
                    loc = recursive_loc(owner, repo_name, data, cache_comment)
                    if loc != 0 and isinstance(loc, (list, tuple)):
                        data[index] = repo_hash + ' ' + str(total_count) + ' ' + str(loc[2]) + ' ' + str(loc[0]) + ' ' + str(loc[1]) + '\n'
            except (TypeError, KeyError, AttributeError, IndexError):
                data[index] = repo_hash + ' 0 0 0 0\n'
    with open(filename, 'w') as f:
        f.writelines(cache_comment)
        f.writelines(data)
    for line in data:
        loc = line.split()
        if len(loc) >= 5:
            loc_add += int(loc[3])
            loc_del += int(loc[4])
    return [loc_add, loc_del, loc_add - loc_del, cached]

def flush_cache(edges, filename, comment_size):
    data = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            if comment_size > 0:
                data = f.readlines()[:comment_size]
    with open(filename, 'w') as f:
        f.writelines(data)
        for node in edges:
            if node and isinstance(node, dict) and node.get('node') and 'nameWithOwner' in node['node']:
                f.write(hashlib.sha256(node['node']['nameWithOwner'].encode('utf-8')).hexdigest() + ' 0 0 0 0\n')

def force_close_file(data, cache_comment):
    filename = 'cache/'+hashlib.sha256(USER_NAME.encode('utf-8')).hexdigest()+'.txt'
    with open(filename, 'w') as f:
        f.writelines(cache_comment)
        f.writelines(data)
    print('Error saving.')

def stars_counter(data):
    total_stars = 0
    if not data:
        return 0
    for node in data:
        if node and isinstance(node, dict):
            repo_node = node.get('node')
            if repo_node and isinstance(repo_node, dict):
                stargazers = repo_node.get('stargazers')
                if stargazers and isinstance(stargazers, dict):
                    total_stars += stargazers.get('totalCount', 0)
    return total_stars

def get_language_breakdown():
    query_count('language_breakdown')
    query = '''
    query($login: String!) {
        user(login: $login) {
            repositories(first: 100, ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER], isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
                nodes {
                    languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                        edges {
                            size
                            node {
                                name
                            }
                        }
                    }
                }
            }
        }
    }'''
    request = simple_request('language_breakdown', query, {'login': USER_NAME})
    res_json = request.json()
    user_data = res_json.get('data', {}).get('user') if res_json.get('data') else None
    if not user_data or not user_data.get('repositories'):
        return "None", "", ""
    repos = user_data['repositories'].get('nodes', []) or []
    langs = {}
    for repo in repos:
        if repo and isinstance(repo, dict) and repo.get('languages') and repo['languages'].get('edges'):
            for edge in repo['languages']['edges']:
                if edge and isinstance(edge, dict) and edge.get('node') and 'name' in edge['node'] and 'size' in edge:
                    name = edge['node']['name']
                    size = edge.get('size', 0)
                    langs[name] = langs.get(name, 0) + size
    sorted_langs = sorted(langs.items(), key=lambda item: item[1], reverse=True)
    if not sorted_langs:
        return "None", "", ""
    total_size = sum([l[1] for l in sorted_langs])
    if total_size == 0:
        return "None", "", ""
    top = []
    for l in sorted_langs:
        pct = round((l[1] / total_size) * 100)
        if pct > 0:
            top.append(f"{l[0]} {pct}%")
    line1 = ", ".join(top[:4]) if top[:4] else "None"
    line2 = ", ".join(top[4:7]) if top[4:7] else ""
    line3 = ", ".join(top[7:10]) if top[7:10] else ""
    return line1, line2, line3

def get_recent_activity():
    query_count('recent_activity')
    request = requests.get(f'https://api.github.com/users/{USER_NAME}/events', headers=HEADERS)
    if request.status_code == 200:
        events = request.json()
        if isinstance(events, list):
            for event in events:
                if isinstance(event, dict) and event.get('type') == 'PushEvent' and event.get('actor', {}).get('login') == USER_NAME:
                    repo = event.get('repo', {})
                    repo_name = repo.get('name', '').split('/')[-1]
                    if repo_name:
                        return f"Pushed to {repo_name}"
    return "None"

def get_medium_stats(username):
    # Medium RSS feed only returns up to 10 articles and doesn't expose claps.
    # Using user-provided values:
    articles = "15"
    claps = "14" # Update this value with your actual claps
    return articles, claps

def svg_overwrite(filename, age_data, commit_data, star_data, repo_data, contrib_data, follower_data, loc_data, lang_data, recent_data, medium_data):
    tree = etree.parse(filename)
    root = tree.getroot()
    find_and_replace(root, 'commit_data', commit_data)
    find_and_replace(root, 'star_data', star_data)
    find_and_replace(root, 'repo_data', repo_data)
    find_and_replace(root, 'contrib_data', contrib_data)
    find_and_replace(root, 'follower_data', follower_data)
    find_and_replace(root, 'loc_data', loc_data[2])
    find_and_replace(root, 'loc_add', loc_data[0])
    find_and_replace(root, 'loc_del', loc_data[1])
    
    # New fields
    find_and_replace(root, 'age_data', age_data)
    find_and_replace(root, 'lang_data', lang_data[0] if len(lang_data) > 0 else "")
    find_and_replace(root, 'lang_data_2', lang_data[1] if len(lang_data) > 1 else "")
    find_and_replace(root, 'lang_data_3', lang_data[2] if len(lang_data) > 2 else "")
    find_and_replace(root, 'recent_data', recent_data)
    find_and_replace(root, 'medium_articles', medium_data[0])
    find_and_replace(root, 'medium_claps', medium_data[1])

    tree.write(filename, encoding='utf-8', xml_declaration=True)

def find_and_replace(root, element_id, new_text):
    element = root.find(f".//*[@id='{element_id}']")
    if element is not None:
        if isinstance(new_text, int):
            new_text = f"{'{:,}'.format(new_text)}"
        element.text = str(new_text)

def commit_counter(comment_size):
    total_commits = 0
    filename = 'cache/'+hashlib.sha256(USER_NAME.encode('utf-8')).hexdigest()+'.txt'
    if not os.path.exists(filename):
        return 0
    with open(filename, 'r') as f:
        data = f.readlines()
    data = data[comment_size:]
    for line in data:
        parts = line.split()
        if len(parts) >= 3:
            total_commits += int(parts[2])
    return total_commits

def user_getter(username):
    query_count('user_getter')
    query = '''
    query($login: String!){
        user(login: $login) {
            id
            createdAt
        }
    }'''
    variables = {'login': username}
    request = simple_request(user_getter.__name__, query, variables)
    user_data = request.json().get('data', {}).get('user')
    if not user_data:
        raise Exception(f"User {username} not found: {request.text}")
    return {'id': user_data['id']}, user_data['createdAt']

def follower_getter(username):
    query_count('follower_getter')
    query = '''
    query($login: String!){
        user(login: $login) {
            followers {
                totalCount
            }
        }
    }'''
    request = simple_request(follower_getter.__name__, query, {'login': username})
    user_data = request.json().get('data', {}).get('user')
    if not user_data or not user_data.get('followers'):
        return 0
    return int(user_data['followers']['totalCount'])

def query_count(funct_id):
    global QUERY_COUNT
    QUERY_COUNT[funct_id] += 1

def perf_counter(funct, *args):
    start = time.perf_counter()
    funct_return = funct(*args)
    return funct_return, time.perf_counter() - start

if __name__ == '__main__':
    user_data, user_time = perf_counter(user_getter, USER_NAME)
    OWNER_ID, acc_date = user_data
    
    # Ankit Arsh Birthday
    age_data, age_time = perf_counter(daily_readme, datetime.datetime(2004, 7, 19))
    
    total_loc, loc_time = perf_counter(loc_query, ['OWNER', 'COLLABORATOR', 'ORGANIZATION_MEMBER'], 7)
    commit_data, commit_time = perf_counter(commit_counter, 7)
    star_data, star_time = perf_counter(graph_repos_stars, 'stars', ['OWNER'])
    repo_data, repo_time = perf_counter(graph_repos_stars, 'repos', ['OWNER'])
    contrib_data, contrib_time = perf_counter(graph_repos_stars, 'repos', ['OWNER', 'COLLABORATOR', 'ORGANIZATION_MEMBER'], None, 0, 0, False)
    follower_data, follower_time = perf_counter(follower_getter, USER_NAME)
    
    # New metrics
    lang_data, lang_time = perf_counter(get_language_breakdown)
    recent_data, recent_time = perf_counter(get_recent_activity)
    medium_data, medium_time = perf_counter(get_medium_stats, 'ankitarsh19')

    for index in range(len(total_loc)-1): total_loc[index] = '{:,}'.format(total_loc[index])

    svg_overwrite('dark_mode.svg', age_data, commit_data, star_data, repo_data, contrib_data, follower_data, total_loc[:-1], lang_data, recent_data, medium_data)
    svg_overwrite('light_mode.svg', age_data, commit_data, star_data, repo_data, contrib_data, follower_data, total_loc[:-1], lang_data, recent_data, medium_data)