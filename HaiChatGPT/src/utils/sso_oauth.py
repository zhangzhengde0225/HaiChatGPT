
import os, sys
from pathlib import Path
import shutil
import json
import ldap

SEARCH_BASE = "ou=users,dc=ihep,dc=ac,dc=cn"

class SSOAuth(object):
    """
    sso oauth based on ldap
    Usage：
    >>> ssoauth = SSOAuth()
    >>> ssoauth.verify_user(username, password)
    第一次使用需要输入server, admin_name, admin_passwd, 保存在~/.config/sso_oauth/config.json中
    """
    def __init__(self) -> None:
        self.config_file = f'{Path.home()}/.config/sso_oauth/config.json'
        self.config = self.load_config()

        self._ldapconn = None

    def verify_user(self, username, passwd):
        """
        return True if username and passwd are correct
        """
        searchScope = ldap.SCOPE_SUBTREE    #查找范围，不用管系统定义
        searchFilter = "(cn=%s)" % username   #用户邮箱设定
        ldap_result = self.ldapconn.search_s(SEARCH_BASE, searchScope, searchFilter, None)  #查找语句
        if ldap_result:
            user_dn = ldap_result[0][0]
            try:
                self.ldapconn.simple_bind_s(user_dn, passwd)
                return True
            except ldap.LDAPError as e:
                return False
        else:
            raise NameError('unkown ldap error')

    @property
    def ldapconn(self):
        if self._ldapconn is None:
            self._ldapconn = ldap.initialize(self.ldap_server)  # 初始化ldap服务器
            self._ldapconn.simple_bind_s(
                f"cn={self.admin_name},ou=users,dc=ihep,dc=ac,dc=cn", 
                self.admin_password)
            self._ldapconn
        return self._ldapconn

    @property
    def ldap_server(self):
        if self.config['ldap_server'] in ['ldap://', '']:
            # 输入ldap服务器地址
            server = input('ldap server: \nldap://')
            self.config['ldap_server'] = f'ldap://{server}'
            self.save_config(self.config)
        return self.config['ldap_server']
    
    @property
    def admin_name(self):
        if self.config['admin_name'] in ['',]:
            # 输入ldap管理员用户名
            name = input('ldap admin name: \n')
            self.config['admin_name'] = name
            self.save_config(self.config)
        return self.config['admin_name']
    
    @property
    def admin_password(self):
        if self.config['admin_password'] in ['',]:
            # 输入ldap管理员密码
            passwd = input('ldap admin password: \n')
            self.config['admin_password'] = passwd
            self.save_config(self.config)
        return self.config['admin_password']

    def load_config(self):
        if not os.path.exists(self.config_file):
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            empty_config = {
                'ldap_server': 'ldap://',
                'admin_name': '',
                'admin_password': '',
                },
            self.save_config(empty_config)
            self.load_config()
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    
    def save_config(self, config):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

