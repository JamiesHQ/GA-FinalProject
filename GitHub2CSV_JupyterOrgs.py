"""
4/2/2017 This is a work in progress and might be abandonded for getorg. The token has been updated to current but nothing else. 

originally from https://gist.github.com/unbracketed/3380407#file-export_repo_issues_to_csv-py-L34
Exports Issues from a specified repository to a CSV file
Uses basic authentication (Github username + password) to retrieve Issues
from a repository that username has access to. Supports Github API v3.
token 1ca9cfcf3a0f1922b95c582ff5fe5273d4c2a9a6

C:\Python27\python.exe C:\Users\e5jym7b\Desktop\Git2CSV_jsw_labels.py
"""
import csv
import requests
import datetime

GITHUB_USER = ''
GITHUB_PASSWORD = ''
REPO = 'Carnegie/RelayHealth.DataPlatform'  # format is username/repo
ISSUES_FOR_REPO_URL = 'http://ndhaxpgit01.mckesson.com/api/v3/repos/%s/issues?access_token=1ca9cfcf3a0f1922b95c582ff5fe5273d4c2a9a6' % REPO
AUTH = (GITHUB_USER, GITHUB_PASSWORD)
WRITTEN = []

def fmt_date(timestring):
    time_tuple = datetime.datetime.strptime(timestring,'%Y-%m-%dT%H:%M:%SZ')
    return time_tuple.strftime('%Y-%m-%d')
    
def write_issues(response):
    "output a list of issues to csv"
    if not response.status_code == 200:
        raise Exception(response.status_code)
    for issue in response.json():
        milestone = issue['milestone']
        milestone_title = ''
        milestone_due_on = ''
        if milestone is not None:
            milestone_title = milestone['title'].encode('utf-8')
            milestone_due_on = milestone['due_on']
        labels = issue['labels']
        label_names = ""
        if labels is not None:
            for label in labels:
                if label is not None:
                    if label['name'] in ['Do', 'Doing', 'Done', 'Dont', 'Feat - Configuration', 'Feat - Deployments', 'Feat - Doc', 
                        'Feat - Eventing', 'Feat - GraphEngine', 'Feat - MgmtTools', 'Feat - Runtime', 'Feat - Storage', 
                        'Priority - High', 'Priority - Low', 'Priority - Medium', 'Size - Large', 'Size - Medium', 'Size - Small', 
                        'Type - Bug', 'Type - Duplicate', 'Type - Enhancement', 'Type - Invalid', 'Type - New Feature', 'Type - Obsoletion', 
                        'Type - Question', 'Type - Testing']:
                        if label_names == "":
                            label_names = label['name']
                        else:
                            label_names = "|".join([label_names, label['name']])
        csvout.writerow([label_names.encode('utf-8'), issue['number'], issue['title'].encode('utf-8'), fmt_date(issue['created_at']), fmt_date(issue['updated_at']), milestone_title, milestone_due_on])


r = requests.get(ISSUES_FOR_REPO_URL, auth=AUTH)
csvfile = '%s-labels.csv' % (REPO.replace('/', '-'))
csvout = csv.writer(open(csvfile, 'wb'))
csvout.writerow(('Labels', 'id', 'Title', 'Created At', 'Updated At',  'milestone_title', 'milestone_due_on'))
write_issues(r)

#more pages? examine the 'link' header returned
last_one = False
def get_next_page(response):
    global last_one
    if 'link' in response.headers:
        pages = dict(
            [(rel[6:-1], url[url.index('<')+1:-1]) for url, rel in
                [link.split(';') for link in
                    response.headers['link'].split(',')]])
        print pages
        if 'last' in pages and 'next' in pages:
            if pages['last'] == pages['next']:
                if last_one is False:
                    last_one = True
                    return pages['next']
                else:
                    return None
            else:
                return pages['next']
        else:
            return None
    else:
        return None
        
while True:
    next = get_next_page(r)
    if next is None:
        break

    r = requests.get(next)
    write_issues(r)
