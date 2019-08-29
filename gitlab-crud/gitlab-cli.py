# /usr/bin/python
# coding=utf-8

# 参考
# https://python-gitlab.readthedocs.io
# https://gitpython.readthedocs.io/en/stable/


import time
import os
import gitlab
from git import *

##定义python-gitlab使用的配置名称
##https://python-gitlab.readthedocs.io/en/stable/cli.html#configuration
python_gitlab_conf_name = 'forest10'


class GitlabAPI(object):
    def __init__(self, *args, **kwargs):
        if os.path.exists('/etc/python-gitlab.cfg'):
            self.gl = gitlab.Gitlab.from_config(python_gitlab_conf_name, ['/etc/python-gitlab.cfg'])
        elif os.path.exists(os.getenv('HOME') + '/.python-gitlab.cfg'):
            self.gl = gitlab.Gitlab.from_config(python_gitlab_conf_name, [os.getenv('HOME') + '/.python-gitlab.cfg'])
        else:
            print('You need to make sure there is a file named "/etc/python-gitlab.cfg" or "~/.python-gitlab.cfg"')
            sys.exit(5)

    def get_projects_ssh_url(self):
        ## login
        # list all the projects
        # gl.projects.list(all=True) error use per_page=100 instead
        projects = self.gl.projects.list()
        result_list = []
        for project in projects:
            result_list.append(project.ssh_url_to_repo)
        return result_list

    def get_my_groupIds(self):
        groups = self.gl.groups.list()
        result_list = []
        for group in groups:
            result_list.append(group.id)
        return result_list

    def get_projects_by_owned_groups(self, groupId):
        group = self.gl.groups.get(groupId)
        print('')
        print('群组名称:{}'.format(group.name))
        projects = group.projects.list()
        result_list = []
        for project in projects:
            result_list.append(project.ssh_url_to_repo)
        return result_list


def _do_git_clone_or_pull(git_url, to_dir):
    name = git_url.split('/')[1].split('.')[0]
    if to_dir.endswith('/'):
        to_dir = to_dir
    else:
        to_dir = to_dir + '/'
    to_path = to_dir + name
    if os.path.exists(to_path):
        print(to_path + '已存在')
    else:
        print(name + '执行clone')
        Repo.clone_from(url=git_url, to_path=to_path)

    repo = Repo.init(path=to_path)
    try:
        repo.git.checkout('master')
    except GitCommandError:
        print('master不存在')
        return
    # 创建remote：
    remote = repo.remote()
    # 切换master
    repo.heads.master.checkout()
    print('开始执行git master pull')
    # 执行pull
    remote.pull()


# tableNameList需要查找的数据库表名,空格分割;findDir需要查找的最上层文件夹目录
def _find_table_use_in_project(textList, findDir, regressionFile='*.xml'):
    print('开始搜索表....' + tableNameList)
    # textList作为一个整参数做传递
    os.system('../shell/findTextInProject.sh ' + '\'' + textList + '\'' + ' ' + findDir + ' ' + regressionFile)
    print('搜索完毕')


def _do_get_all_my_project_master(to_dir):
    local_gitlab = GitlabAPI()
    result_list = []
    groups = local_gitlab.get_my_groupIds()
    for groupId in groups:
        projects = local_gitlab.get_projects_by_owned_groups(groupId)
        for sshUrl in projects:
            result_list.append(sshUrl)
            _do_git_clone_or_pull(sshUrl, to_dir)

    print('>>>>>>>warning<<<<<<<<')
    print('共操作{}个工程,请确保自己是管理员或已经加入了所有需搜索工程的权限,否则搜索不完全!!!'.format(len(result_list)))
    print('>>>>>>>warning<<<<<<<<')


if __name__ == '__main__':
    # 1.定义最终放置所有工程的目标文件夹
    find_dir = os.getenv('HOME') + '/Desktop/py-git'
    # 2.整体做git pull或者clone操作
    _do_get_all_my_project_master(find_dir)
    # 等待一两秒执行git pull
    time.sleep(3)
    # 3.定义需要查找的文本,空格分割; 'haha 呵呵'
    tableNameList = 'haha 呵呵'
    # 4.执行搜索
    _find_table_use_in_project(tableNameList, find_dir)
