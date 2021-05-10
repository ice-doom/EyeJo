CREATE DATABASE IF NOT EXISTS EyeJo;
USE EyeJo;

CREATE TABLE `project` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '新建项目id',
  `name` varchar(255) NOT NULL COMMENT '项目名称',
  `create_time` datetime NOT NULL COMMENT '项目创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `url_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `project_id` int(11) DEFAULT 0 COMMENT '对应的项目ID',
  `url` varchar(550) DEFAULT NULL COMMENT 'URL地址',
  `status_code` varchar(4) DEFAULT NULL COMMENT '状态码',
  `icons` varchar(500) DEFAULT NULL COMMENT 'icons路径',
  `icons_hash` varchar(32) DEFAULT NULL COMMENT 'icons的hash',
  `pic` varchar(500) DEFAULT NULL COMMENT '截图图片路径',
  `pic_hash` varchar(32) DEFAULT NULL COMMENT '截图图片hash',
  `title` varchar(200)  DEFAULT NULL COMMENT '访问页面的title',
  `headers` varchar(5000)  DEFAULT NULL COMMENT '访问页面的headers',
  `html` varchar(600) DEFAULT NULL COMMENT 'html源码路径',
  `html_copyright` varchar(600) DEFAULT NULL COMMENT '页面的copyright',
  `ssl_Organization` varchar(255) DEFAULT NULL COMMENT 'ssl证书信息',
  `finger` varchar(2000) DEFAULT "{}" COMMENT '指纹识别',
  `screen_status` varchar(50) DEFAULT NULL COMMENT '标记截图是否成功的状态',
  PRIMARY KEY (`id`) USING BTREE,
  CONSTRAINT `url_project_fk` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `project_id` int(11) DEFAULT 0 COMMENT '对应的项目ID',
  `name` varchar(255) NOT NULL COMMENT 'tag名称',
  `url_info_id` int(11) NOT NULL COMMENT '',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_tags (name, url_info_id, project_id),
  CONSTRAINT `tags_url_info_fk` FOREIGN KEY (`url_info_id`) REFERENCES `url_info` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tags_project_fk` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `subdomain` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `project_id` int(11) NOT NULL COMMENT '项目ID',
  `subdomain` varchar(260) DEFAULT NULL COMMENT '子域名',
  `m_domain` varchar(260) DEFAULT NULL COMMENT '解析得到的主域名',
  `cname` varchar(500) DEFAULT NULL COMMENT 'cname记录',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_subdomain (project_id, subdomain, m_domain),
  CONSTRAINT `subdomain_project_fk` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `ipaddress` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'IP地址id',
  `project_id` int(11) NOT NULL COMMENT '项目ID',
  `ip_address` varchar(20) DEFAULT NULL COMMENT 'IP地址',
  `country` varchar(255) DEFAULT NULL COMMENT 'IP所属国家',
  `regionName` varchar(255) DEFAULT NULL COMMENT 'IP所属省',
  `city` varchar(255) DEFAULT NULL COMMENT 'IP所属城市',
  `isp` varchar(255) DEFAULT NULL COMMENT 'IP所属运营商',
  `asn` varchar(255) DEFAULT NULL COMMENT 'ASN号',
  `cdn` int(1) DEFAULT 0 COMMENT 'CDN',
  `flag` int(1) DEFAULT 0 COMMENT 'flag',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_ipaddress (project_id, ip_address),
  CONSTRAINT `ip_project_fk` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `ip_domain_relationship` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `ip_id` int(11) DEFAULT NULL COMMENT '项目ID',
  `subdomain_id` int(11) DEFAULT NULL COMMENT '域名表id',
  PRIMARY KEY (`id`) USING BTREE,
  CONSTRAINT `relation_ip_fk` FOREIGN KEY (`ip_id`) REFERENCES `ipaddress` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `relation_domain_fk` FOREIGN KEY (`subdomain_id`) REFERENCES `subdomain` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `port` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '端口id',
  `ip_id` int(11) DEFAULT NULL COMMENT 'IP地址id',
  `port` varchar(10) DEFAULT NULL COMMENT '端口号',
  `protocol` varchar(255) DEFAULT NULL COMMENT '协议类型',
  `product` varchar(255) DEFAULT NULL,
  `version` varchar(255) DEFAULT NULL,
  `extrainfo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_port (ip_id, port),
  CONSTRAINT `port_ip_fk` FOREIGN KEY (`ip_id`) REFERENCES `ipaddress` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- FOREIGN KEY(ip_address) REFERENCES t_ipaddress(ip_address),
-- ALTER TABLE t_port ADD FOREIGN KEY t_port_t_ipaddress_1 (ip_address) REFERENCES t_ipaddress (ip_address);


CREATE TABLE `asset` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '资产id',
  `project_id` int(11) NOT NULL COMMENT '项目ID',
  `name` varchar(255) NOT NULL COMMENT '资产名称',
  `create_time` datetime NOT NULL COMMENT '资产创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_asset (project_id, name),
  CONSTRAINT `asset_project_fk` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- 只有前台展示的时候会从里面提取输入的目标原始内容

CREATE TABLE `asset_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '资产组的唯一标识',
  `asset_id` int(11) NOT NULL COMMENT '资产组名称',
  `url` varchar(550) NOT NULL COMMENT '地址',
  `status` varchar(20) DEFAULT NULL COMMENT '存活状态',
  `create_time` datetime NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_asset_group (asset_id, url),
  CONSTRAINT `asset_group_asset_fk` FOREIGN KEY (`asset_id`) REFERENCES `asset` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

CREATE TABLE `task` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '任务的唯一标识',
  `project_id` int(11) NOT NULL COMMENT '项目ID',
  `name` varchar(255) NOT NULL COMMENT '任务名',
  `status` varchar(40) NOT NULL COMMENT '状态',
  `option_subdomain_collect` varchar(10) NOT NULL COMMENT '子域名收集选项',
  `option_port_scan` varchar(10) NOT NULL COMMENT '端口扫描选项',
  `option_ports` varchar(10000) NOT NULL COMMENT '端口号',
  `option_sf_info` varchar(10) NOT NULL COMMENT 'shodan和fofa选项',
  `option_fofa_search` varchar(550) NOT NULL COMMENT 'fofa搜索内容',
  `option_screen_info` varchar(10) NOT NULL COMMENT '截图选项',
  `option_request_site` varchar(10) NOT NULL COMMENT '请求站点选项',
  `option_poc_scan` varchar(10) NOT NULL COMMENT 'POC检测选项',
  `option_pocss` longtext NOT NULL COMMENT 'POC名称',
  `option_fuzz` varchar(10) NOT NULL COMMENT 'FUZZ选项',
  `option_fuzz_file` varchar(100) NOT NULL COMMENT 'FUZZ文件',
  `option_identify_login` varchar(10) NOT NULL COMMENT '登录口识别选项',
  `option_vul` varchar(10) NOT NULL COMMENT '漏洞检测选项',
  `option_brute` varchar(10) NOT NULL COMMENT '服务爆破选项',
  `option_brute_type` varchar(200) NOT NULL COMMENT '选择的服务爆破类型',
  `celery_id` varchar(40) NOT NULL COMMENT 'celery唯一标识',
  `create_time` datetime NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `end_time` datetime NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '结束时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

CREATE TABLE `asset_task_relationship` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'IP地址id',
  `asset_group_id` int(11) NOT NULL COMMENT '资产组ID',
  `task_id` int(11) NOT NULL COMMENT '任务id',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_asset_task (asset_group_id, task_id),
  CONSTRAINT `relation_asset_fk` FOREIGN KEY (`asset_group_id`) REFERENCES `asset_group` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `relation_task_fk` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

CREATE TABLE `poc_check` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'poc的检测的唯一标识id',
  `task_id` int(11) NOT NULL COMMENT '任务的唯一标识',
  `poc_url` varchar(550) NOT NULL COMMENT 'poc检测的URL地址',
  `result_code` varchar(10) NOT NULL COMMENT 'POC检测结果',
  `poc_name` varchar(255) NOT NULL COMMENT 'POC名称',
  `verifyinfo` varchar(255) NOT NULL COMMENT 'POC检测内容',
  `create_time` datetime NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  CONSTRAINT `poc_task_fk` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

  -- `target` varchar(550) DEFAULT NULL COMMENT 'target表目标的地址',
  -- `ipaddress_id` int(11) DEFAULT NULL COMMENT 'ipaddress的id',

CREATE TABLE `fuzz` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'fuzz的唯一标识id',
  `url` varchar(550) NOT NULL COMMENT 'fuzz目标的URL地址',
  `fuzz_url` varchar(550) NOT NULL COMMENT 'fuzz结果的URL地址',
  `task_id` int(11) NOT NULL COMMENT '任务的唯一标识',
  `status_code` int(4) NOT NULL COMMENT 'HTTP状态码',
  `lines` int(11) NOT NULL COMMENT '响应包行数',
  `words` int(11) NOT NULL COMMENT '响应包字符数',
  `create_time` datetime NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  CONSTRAINT `fuzz_task_fk` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `vulnerability` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '漏洞的唯一标识id',
  `task_id` int(11) NOT NULL COMMENT '任务的唯一标识',
  `url` varchar(550) NOT NULL COMMENT '漏洞URL地址',
  `payload` varchar(3000) NOT NULL COMMENT '漏洞利用的payload',
  `snapshot_req` longtext NOT NULL COMMENT '请求数据',
  `vulntype` varchar(100) NOT NULL COMMENT '漏洞类型',
  `scan_name` varchar(20) NOT NULL COMMENT '使用的扫描器名称',
  `create_time` datetime NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  CONSTRAINT `vul_task_fk` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `crawl` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '爬虫的唯一标识id',
  `task_id` int(11) NOT NULL COMMENT '任务的唯一标识',
  `url` varchar(255) NOT NULL COMMENT 'URL地址',
  `crawl_url` varchar(5000) NOT NULL COMMENT 'URL地址',
  `method` varchar(5) NOT NULL COMMENT '请求类型',
  `headers` varchar(2000) NOT NULL COMMENT '请求头',
  `req_data` varchar(5000) DEFAULT NULL COMMENT '请求数据',
  `is_login` int(1) DEFAULT 0 COMMENT '是否是登录接口',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  CONSTRAINT `crawl_task_fk` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `login_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '登录识别的唯一标识id',
  `task_id` int(11) NOT NULL COMMENT '任务的唯一标识',
  `url` varchar(550) DEFAULT NULL COMMENT '登录URL地址',
  `crawl_id` int(11) DEFAULT NULL COMMENT '爬虫的唯一标识',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_login_site (task_id, crawl_id),
  CONSTRAINT `login_site_crawl_fk` FOREIGN KEY (`crawl_id`) REFERENCES `crawl` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `login_site_task_fk` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `brute` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '爆破表的唯一标识id',
  `task_id` int(11) NOT NULL COMMENT '任务的唯一标识',
  `ip_address` varchar(20) NOT NULL COMMENT 'IP地址',
  `port` varchar(10) NOT NULL COMMENT '端口号',
  `service` varchar(255) NOT NULL COMMENT '服务类型',
  `username` varchar(100) NOT NULL COMMENT '用户名',
  `password` varchar(100) NOT NULL COMMENT '密码',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_brute (task_id, ip_address, port),
  CONSTRAINT `brute_task_fk` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `side_station` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '旁站的唯一标识id',
  `ip_address` varchar(20) NOT NULL COMMENT 'IP地址',
  `subdomain` varchar(260) NOT NULL COMMENT '域名',
  `title` varchar(200)  DEFAULT NULL COMMENT '访问页面的title',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_side_station (ip_address, subdomain)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `c_net` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'C段的唯一标识id',
  `ip_address` varchar(20) NOT NULL COMMENT 'IP地址',
  `ip_c` varchar(20) NOT NULL COMMENT '所属C段',
  `title` varchar(200)  DEFAULT NULL COMMENT '访问页面的title',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY uk_c_net (ip_address, ip_c)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;


CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



