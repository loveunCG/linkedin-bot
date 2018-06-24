-- MySQL dump 10.13  Distrib 5.7.22, for Linux (x86_64)
--
-- Host: 10.0.0.15    Database: sq_jetbuzz_db
-- ------------------------------------------------------
-- Server version	5.7.21

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `app_bottask`
--

DROP TABLE IF EXISTS `app_bottask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_bottask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_type` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `status` varchar(20) NOT NULL,
  `lastrun_date` datetime(6) DEFAULT NULL,
  `completed_date` datetime(6) DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  `extra_info` longtext,
  `extra_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `app_bottask_owner_id_6d10f842_fk_app_linkedinuser_id` (`owner_id`),
  CONSTRAINT `app_bottask_owner_id_6d10f842_fk_app_linkedinuser_id` FOREIGN KEY (`owner_id`) REFERENCES `app_linkedinuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=169 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_linkedinuser`
--

DROP TABLE IF EXISTS `app_linkedinuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_linkedinuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `password` varchar(32) NOT NULL,
  `latest_login` datetime(6) DEFAULT NULL,
  `status` tinyint(1) NOT NULL,
  `is_weekendwork` tinyint(1) NOT NULL,
  `start_from` int(11) NOT NULL,
  `start_to` int(11) NOT NULL,
  `tz` varchar(50) NOT NULL,
  `user_id` int(11) NOT NULL,
  `login_status` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_linkedinuser_email_2a47a7ae_uniq` (`email`),
  KEY `app_linkedinuser_user_id_2219698b_fk_auth_user_id` (`user_id`),
  CONSTRAINT `app_linkedinuser_user_id_2219698b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_linkedinuser_membership`
--

DROP TABLE IF EXISTS `app_linkedinuser_membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_linkedinuser_membership` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `linkedinuser_id` int(11) NOT NULL,
  `membership_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_linkedinuser_members_linkedinuser_id_membersh_ca45731a_uniq` (`linkedinuser_id`,`membership_id`),
  KEY `app_linkedinuser_mem_membership_id_71fa9f2f_fk_app_membe` (`membership_id`),
  CONSTRAINT `app_linkedinuser_mem_linkedinuser_id_638ff280_fk_app_linke` FOREIGN KEY (`linkedinuser_id`) REFERENCES `app_linkedinuser` (`id`),
  CONSTRAINT `app_linkedinuser_mem_membership_id_71fa9f2f_fk_app_membe` FOREIGN KEY (`membership_id`) REFERENCES `app_membership` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_membership`
--

DROP TABLE IF EXISTS `app_membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_membership` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `valid_from` datetime(6) DEFAULT NULL,
  `valid_to` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `membership_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_membership_user_id_77986dfe_fk_auth_user_id` (`user_id`),
  KEY `app_membership_membership_type_id_724f1423_fk_app_membe` (`membership_type_id`),
  CONSTRAINT `app_membership_membership_type_id_724f1423_fk_app_membe` FOREIGN KEY (`membership_type_id`) REFERENCES `app_membershiptype` (`id`),
  CONSTRAINT `app_membership_user_id_77986dfe_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_membershiptype`
--

DROP TABLE IF EXISTS `app_membershiptype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_membershiptype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` longtext,
  `max_seat` int(11) NOT NULL,
  `max_search` int(11) NOT NULL,
  `company_title_search` tinyint(1) NOT NULL,
  `custom_connect_message` tinyint(1) NOT NULL,
  `day_to_live` int(11) NOT NULL,
  `export_csv` tinyint(1) NOT NULL,
  `max_campaign` int(11) NOT NULL,
  `max_search_result` int(11) NOT NULL,
  `price` double NOT NULL,
  `twoway_comm` tinyint(1) NOT NULL,
  `welcome_message` tinyint(1) NOT NULL,
  `withdrawn_invite` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `connector_connectmessage`
--

DROP TABLE IF EXISTS `connector_connectmessage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `connector_connectmessage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `update_at` datetime(6) NOT NULL,
  `text` longtext NOT NULL,
  `time` datetime(6) NOT NULL,
  `type` varchar(50) NOT NULL,
  `connector_id` int(11) DEFAULT NULL,
  `requestee_id` int(11) DEFAULT NULL,
  `is_connected` tinyint(1) NOT NULL,
  `is_replied_other` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `connector_connectmes_connector_id_f7a1d6b5_fk_connector` (`connector_id`),
  KEY `connector_connectmes_requestee_id_05e3a974_fk_messenger` (`requestee_id`),
  CONSTRAINT `connector_connectmes_connector_id_f7a1d6b5_fk_connector` FOREIGN KEY (`connector_id`) REFERENCES `connector_connectorcampaign` (`id`),
  CONSTRAINT `connector_connectmes_requestee_id_05e3a974_fk_messenger` FOREIGN KEY (`requestee_id`) REFERENCES `messenger_inbox` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `connector_connectorcampaign`
--

DROP TABLE IF EXISTS `connector_connectorcampaign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `connector_connectorcampaign` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `connector_name` varchar(200) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `copy_connector_id` int(11) DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `connector_connectorc_copy_connector_id_69ef8055_fk_connector` (`copy_connector_id`),
  KEY `connector_connectorc_owner_id_7ce85a81_fk_app_linke` (`owner_id`),
  CONSTRAINT `connector_connectorc_copy_connector_id_69ef8055_fk_connector` FOREIGN KEY (`copy_connector_id`) REFERENCES `connector_connectorcampaign` (`id`),
  CONSTRAINT `connector_connectorc_owner_id_7ce85a81_fk_app_linke` FOREIGN KEY (`owner_id`) REFERENCES `app_linkedinuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `connector_connectorcampaign_connectors`
--

DROP TABLE IF EXISTS `connector_connectorcampaign_connectors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `connector_connectorcampaign_connectors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `connectorcampaign_id` int(11) NOT NULL,
  `inbox_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `connector_connectorcampa_connectorcampaign_id_sea_aeb62388_uniq` (`connectorcampaign_id`,`inbox_id`),
  KEY `connector_connectorc_inbox_id_15a41ccf_fk_messenger` (`inbox_id`),
  CONSTRAINT `connector_connectorc_connectorcampaign_id_97d346bb_fk_connector` FOREIGN KEY (`connectorcampaign_id`) REFERENCES `connector_connectorcampaign` (`id`),
  CONSTRAINT `connector_connectorc_inbox_id_15a41ccf_fk_messenger` FOREIGN KEY (`inbox_id`) REFERENCES `messenger_inbox` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `connector_connectorstep`
--

DROP TABLE IF EXISTS `connector_connectorstep`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `connector_connectorstep` (
  `campaignstepfield_ptr_id` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `update_at` datetime(6) NOT NULL,
  `campaign_id` int(11) NOT NULL,
  PRIMARY KEY (`campaignstepfield_ptr_id`),
  KEY `connector_connectors_campaign_id_df1fa32b_fk_connector` (`campaign_id`),
  CONSTRAINT `connector_connectors_campaign_id_df1fa32b_fk_connector` FOREIGN KEY (`campaign_id`) REFERENCES `connector_connectorcampaign` (`id`),
  CONSTRAINT `connector_connectors_campaignstepfield_pt_b5eb53ac_fk_messenger` FOREIGN KEY (`campaignstepfield_ptr_id`) REFERENCES `messenger_campaignstepfield` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `connector_search`
--

DROP TABLE IF EXISTS `connector_search`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `connector_search` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `search_name` varchar(254) NOT NULL,
  `keyword` varchar(254) DEFAULT NULL,
  `resultcount` int(11) DEFAULT NULL,
  `searchdate` datetime(6) NOT NULL,
  `company` varchar(254) DEFAULT NULL,
  `industry` varchar(254) DEFAULT NULL,
  `location` varchar(254) DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  `sales_search` varchar(200) DEFAULT NULL,
  `title` varchar(254) DEFAULT NULL,
  `url_search` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `connector_search_owner_id_6a3ce875_fk_app_linkedinuser_id` (`owner_id`),
  CONSTRAINT `connector_search_owner_id_6a3ce875_fk_app_linkedinuser_id` FOREIGN KEY (`owner_id`) REFERENCES `app_linkedinuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `connector_searchresult`
--

DROP TABLE IF EXISTS `connector_searchresult`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `connector_searchresult` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company` varchar(100) DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `industry` varchar(100) DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  `search_id` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `connect_campaign_id` int(11) DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `latest_activity` datetime(6) DEFAULT NULL,
  `linkedin_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `connector_searchresult_company_1dcb8107` (`company`),
  KEY `connector_searchresult_location_776c9bcb` (`location`),
  KEY `connector_searchresult_title_b6619f50` (`title`),
  KEY `connector_searchresult_industry_3e6dd6e5` (`industry`),
  KEY `connector_searchresult_owner_id_d0c2b5fa_fk_app_linkedinuser_id` (`owner_id`),
  KEY `connector_searchresult_search_id_09f56021_fk_connector_search_id` (`search_id`),
  KEY `connector_searchresu_connect_campaign_id_a4c7f16f_fk_messenger` (`connect_campaign_id`),
  KEY `connector_searchresult_name_0d6b015f` (`name`),
  CONSTRAINT `connector_searchresu_connect_campaign_id_a4c7f16f_fk_messenger` FOREIGN KEY (`connect_campaign_id`) REFERENCES `messenger_campaign` (`id`),
  CONSTRAINT `connector_searchresult_owner_id_d0c2b5fa_fk_app_linkedinuser_id` FOREIGN KEY (`owner_id`) REFERENCES `app_linkedinuser` (`id`),
  CONSTRAINT `connector_searchresult_search_id_09f56021_fk_connector_search_id` FOREIGN KEY (`search_id`) REFERENCES `connector_search` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=157 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `connector_taskqueue`
--

DROP TABLE IF EXISTS `connector_taskqueue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `connector_taskqueue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(20) NOT NULL,
  `object_id` int(10) unsigned NOT NULL,
  `queue_type_id` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `remark` longtext,
  `due_date` datetime(6),
  PRIMARY KEY (`id`),
  KEY `connector_taskqueue_queue_type_id_bc9ee02b_fk_django_co` (`queue_type_id`),
  KEY `connector_taskqueue_owner_id_d57384f5_fk_app_linkedinuser_id` (`owner_id`),
  CONSTRAINT `connector_taskqueue_owner_id_d57384f5_fk_app_linkedinuser_id` FOREIGN KEY (`owner_id`) REFERENCES `app_linkedinuser` (`id`),
  CONSTRAINT `connector_taskqueue_queue_type_id_bc9ee02b_fk_django_co` FOREIGN KEY (`queue_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messenger_campaign`
--

DROP TABLE IF EXISTS `messenger_campaign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messenger_campaign` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `update_at` datetime(6) NOT NULL,
  `title` varchar(100) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `copy_campaign_id` int(11) DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  `is_bulk` tinyint(1) NOT NULL,
  `connection_message` longtext,
  `welcome_message` longtext,
  `welcome_time` int(11),
  PRIMARY KEY (`id`),
  KEY `messenger_campaign_title_8ed32cad` (`title`),
  KEY `messenger_campaign_copy_campaign_id_dbb11550_fk_messenger` (`copy_campaign_id`),
  KEY `messenger_campaign_owner_id_a327a81d_fk_app_linkedinuser_id` (`owner_id`),
  CONSTRAINT `messenger_campaign_copy_campaign_id_dbb11550_fk_messenger` FOREIGN KEY (`copy_campaign_id`) REFERENCES `messenger_campaign` (`id`),
  CONSTRAINT `messenger_campaign_owner_id_a327a81d_fk_app_linkedinuser_id` FOREIGN KEY (`owner_id`) REFERENCES `app_linkedinuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messenger_campaign_contacts`
--

DROP TABLE IF EXISTS `messenger_campaign_contacts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messenger_campaign_contacts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `campaign_id` int(11) NOT NULL,
  `inbox_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `messenger_campaign_contacts_campaign_id_contact_id_41a6b7d8_uniq` (`campaign_id`,`inbox_id`),
  KEY `messenger_campaign_c_inbox_id_8186ed78_fk_messenger` (`inbox_id`),
  CONSTRAINT `messenger_campaign_c_campaign_id_ef88725a_fk_messenger` FOREIGN KEY (`campaign_id`) REFERENCES `messenger_campaign` (`id`),
  CONSTRAINT `messenger_campaign_c_inbox_id_8186ed78_fk_messenger` FOREIGN KEY (`inbox_id`) REFERENCES `messenger_inbox` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messenger_campaignstep`
--

DROP TABLE IF EXISTS `messenger_campaignstep`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messenger_campaignstep` (
  `campaignstepfield_ptr_id` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `update_at` datetime(6) NOT NULL,
  `campaign_id` int(11) NOT NULL,
  PRIMARY KEY (`campaignstepfield_ptr_id`),
  KEY `messenger_campaignst_campaign_id_d59b98d1_fk_messenger` (`campaign_id`),
  CONSTRAINT `messenger_campaignst_campaign_id_d59b98d1_fk_messenger` FOREIGN KEY (`campaign_id`) REFERENCES `messenger_campaign` (`id`),
  CONSTRAINT `messenger_campaignst_campaignstepfield_pt_1dc95b23_fk_messenger` FOREIGN KEY (`campaignstepfield_ptr_id`) REFERENCES `messenger_campaignstepfield` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messenger_campaignstepfield`
--

DROP TABLE IF EXISTS `messenger_campaignstepfield`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messenger_campaignstepfield` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `step_number` int(11) NOT NULL,
  `message` longtext NOT NULL,
  `action` varchar(100) NOT NULL,
  `step_time` int(11),
  PRIMARY KEY (`id`),
  KEY `messenger_campaignstepfield_step_number_3622240f` (`step_number`),
  KEY `messenger_campaignstepfield_action_93b4289d` (`action`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messenger_chatmessage`
--

DROP TABLE IF EXISTS `messenger_chatmessage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messenger_chatmessage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `update_at` datetime(6) NOT NULL,
  `text` longtext NOT NULL,
  `time` datetime(6) NOT NULL,
  `type` int(11) NOT NULL,
  `contact_id` int(11) DEFAULT NULL,
  `replied_date` datetime(6) DEFAULT NULL,
  `replied_other_date` datetime(6) DEFAULT NULL,
  `campaign_id` int(11) DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `is_direct` tinyint(1) NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `is_sent` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `messenger_chatmessag_campaign_id_9081ba35_fk_messenger` (`campaign_id`),
  KEY `messenger_chatmessage_contact_id_e0e3dbcc_fk_messenger_inbox_id` (`contact_id`),
  KEY `messenger_chatmessage_owner_id_6e504898_fk_app_linkedinuser_id` (`owner_id`),
  KEY `messenger_chatmessag_parent_id_fa4762ab_fk_messenger` (`parent_id`),
  CONSTRAINT `messenger_chatmessag_campaign_id_9081ba35_fk_messenger` FOREIGN KEY (`campaign_id`) REFERENCES `messenger_campaign` (`id`),
  CONSTRAINT `messenger_chatmessag_parent_id_fa4762ab_fk_messenger` FOREIGN KEY (`parent_id`) REFERENCES `messenger_chatmessage` (`id`),
  CONSTRAINT `messenger_chatmessage_contact_id_e0e3dbcc_fk_messenger_inbox_id` FOREIGN KEY (`contact_id`) REFERENCES `messenger_inbox` (`id`),
  CONSTRAINT `messenger_chatmessage_owner_id_6e504898_fk_app_linkedinuser_id` FOREIGN KEY (`owner_id`) REFERENCES `app_linkedinuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messenger_inbox`
--

DROP TABLE IF EXISTS `messenger_inbox`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messenger_inbox` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company` varchar(100) DEFAULT NULL,
  `industry` varchar(100) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `latest_activity` datetime(6) DEFAULT NULL,
  `status` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  `is_connected` tinyint(1) NOT NULL,
  `linkedin_id` varchar(50) NOT NULL,
  `connected_date` datetime(6) DEFAULT NULL,
  `notes` longtext,
  PRIMARY KEY (`id`),
  KEY `messenger_inbox_owner_id_34b2601d_fk_app_linkedinuser_id` (`owner_id`),
  KEY `messenger_inbox_company_bf154fcd` (`company`),
  KEY `messenger_inbox_industry_3034f0bc` (`industry`),
  KEY `messenger_inbox_location_bb3c0d04` (`location`),
  KEY `messenger_inbox_title_287bafb0` (`title`),
  KEY `messenger_inbox_name_0d599e14` (`name`),
  CONSTRAINT `messenger_inbox_owner_id_34b2601d_fk_app_linkedinuser_id` FOREIGN KEY (`owner_id`) REFERENCES `app_linkedinuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-05-22 18:41:39
