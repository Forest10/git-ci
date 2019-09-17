# /usr/bin/python3
# coding=utf-8

# 参考
# https://python-gitlab.readthedocs.io
# https://gitpython.readthedocs.io/en/stable/

import uuid
import time
import os
import gitlab
from git import *

##定义python-gitlab使用的配置名称
##https://python-gitlab.readthedocs.io/en/stable/cli.html#configuration
python_gitlab_conf_name = 'forest10'
exclude_projects = []


class GitlabAPI(object):
    def __init__(self, *args, **kwargs):
        ## 加载python-gitlab配置
        if os.path.exists('/etc/python-gitlab.cfg'):
            self.gl = gitlab.Gitlab.from_config(python_gitlab_conf_name, ['/etc/python-gitlab.cfg'])
        elif os.path.exists(os.getenv('HOME') + '/.python-gitlab.cfg'):
            self.gl = gitlab.Gitlab.from_config(python_gitlab_conf_name, [os.getenv('HOME') + '/.python-gitlab.cfg'])
        else:
            print('You need to make sure there is a file named "/etc/python-gitlab.cfg" or "~/.python-gitlab.cfg"')
            sys.exit(5)

        ##加载忽略的系统配置(比如某个系统不需要检索.因为现在gitlab只能自己退出群组.不能退出项目)
        if os.path.exists(os.getenv('HOME') + '/.exclude_projects.cfg'):
            with open(os.getenv('HOME') + '/.exclude_projects.cfg', mode='r', encoding='utf-8') as file_obj:
                for line in file_obj.readlines():
                    exclude_projects.append(line.rstrip())
                print('exclude_projects:{}'.format(exclude_projects))
        else:
            print('未发现需要排除的系统配置文件.请确认')

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
    projectName = git_url.split('/')[1].split('.')[0]
    if exclude_projects.__contains__(projectName):
        print(projectName + '配置在排除之列.不进行git操作')
        return
    if to_dir.endswith('/'):
        to_dir = to_dir
    else:
        to_dir = to_dir + '/'
    to_path = to_dir + projectName
    if os.path.exists(to_path):
        print(to_path + '已存在')
    else:
        print(projectName + '执行clone')
        try:
            Repo.clone_from(url=git_url, to_path=to_path)
        except Exception:
            print('clone:{}失败,请确认权限!'.format(projectName))

    repo = Repo.init(path=to_path)
    try:
        repo.git.checkout('master')
    except GitCommandError:
        print('{}master不存在'.format(projectName))
        return
    # 创建remote：
    remote = repo.remote()
    # 切换master
    repo.heads.master.checkout()
    print('{}开始执行git master pull'.format(projectName))
    # 执行pull
    remote.pull()


# textList需要查找的文本list,空格分割;findDir需要查找的最上层文件夹目录
def _find_text_use_in_project(textList, findDir, regressionFile='*.*', ignoreCase='true'):
    print('开始搜索文本....' + textList)
    if (regressionFile.endswith('*')):
        regressionFile = '\'' + regressionFile + '\''
    resultFileName = uuid.uuid1().__str__()
    # textList作为一个整参数做传递
    os.system('../shell/findTextInProject.sh '
              + '\'' + textList + '\''
              + ' ' + findDir
              + ' ' + regressionFile
              + ' ' + ignoreCase
              + ' ' + resultFileName)
    print('搜索完毕')


def _do_get_all_my_project_master(to_dir):
    local_gitlab = GitlabAPI()
    result_list = []
    groups = local_gitlab.get_my_groupIds()
    for groupId in groups:
        projects = local_gitlab.get_projects_by_owned_groups(groupId)
        for sshUrl in projects:
            print('sshUrl:{}'.format(sshUrl))
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
    textList = 'haha 呵呵'
    # 4.执行搜索
    _find_text_use_in_project(textList, find_dir)
